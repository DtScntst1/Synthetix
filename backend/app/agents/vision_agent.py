import logging
import base64
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.database.schema import GraphNode, GraphEdge, VisualInsight
from app.database.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

class VisionExtraction(BaseModel):
    """
    Output schema for the Vision Agent.
    """
    insight: VisualInsight = Field(description="The core insight extracted from the visual chart.")
    related_entities: List[GraphNode] = Field(description="The business/economic entities mentioned in or related to the chart.")
    edges: List[GraphEdge] = Field(description="Relationships linking the entities to the visual insight. Edge type should be 'SUPPORTED_BY_CHART'.")

class VisionAgent:
    def __init__(self):
        # We use Llama-3.2 Vision Preview via Groq (Free/Open Source)
        self.llm = ChatGroq(
            temperature=0.2, # Slight temperature to allow interpreting visual trends
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.2-11b-vision-preview" # Groq's open-source vision model
        ).with_structured_output(VisionExtraction)

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def process_image(self, image_path: str, doc_id: str, page_number: int):
        logger.info(f"Vision Agent parsing image from {doc_id} (Page {page_number})...")
        
        try:
            base64_image = self._encode_image(image_path)
        except Exception as e:
            logger.error(f"Failed to read image {image_path}: {e}")
            return None

        # Build the Multimodal Message for LangChain
        messages = [
            SystemMessage(content=(
                "You are an expert Data Visualizer and GraphRAG Agent. "
                "Your task is to analyze the provided chart or graph image. "
                "1. Identify the 'chart_type' (e.g. Bar Chart, Scatter Plot). "
                "2. Extract the 'key_takeaway' (the most important business insight). "
                "3. Identify the 'trend_direction' if applicable. "
                "4. Extract the real-world entities shown in the chart as GraphNodes. "
                "5. Connect the entities to the insight using GraphEdges (type: 'SUPPORTED_BY_CHART')."
            )),
            HumanMessage(content=[
                {"type": "text", "text": f"Document ID: {doc_id}\nAnalyze this chart and extract the structured data:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ])
        ]

        try:
            extraction: VisionExtraction = await self.llm.ainvoke(messages)
            # Set the source image path
            extraction.insight.source_image_path = image_path
        except Exception as e:
            logger.error(f"Vision Extraction failed: {e}")
            return None

        await neo4j_client.connect()
        try:
            # 1. Insert the Entities
            for node in extraction.related_entities:
                node.source_document_id = doc_id
                node.source_page_number = page_number
                await neo4j_client.create_node(node)
                
            # 2. Insert the Visual Insight as a Node with Label 'ChartInsight'
            insight_node = GraphNode(
                id=f"CHART_{doc_id}_{page_number}",
                label="ChartInsight",
                properties={
                    "chart_type": extraction.insight.chart_type,
                    "key_takeaway": extraction.insight.key_takeaway,
                    "trend_direction": extraction.insight.trend_direction,
                    "source_image_path": extraction.insight.source_image_path
                },
                source_document_id=doc_id,
                source_page_number=page_number
            )
            await neo4j_client.create_node(insight_node)
            logger.info(f"Created Chart Node: {insight_node.id} ({insight_node.properties['trend_direction']})")

            # 3. Insert the Edges
            for edge in extraction.edges:
                # Ensure the edge connects to the new chart node if it's the target
                if edge.target_id == "INSIGHT":
                    edge.target_id = insight_node.id
                await neo4j_client.create_edge(edge)
                logger.info(f"Created Vision Edge: {edge.source_id} -[{edge.type}]-> {edge.target_id}")

        except Exception as e:
            logger.error(f"Vision Database insertion failed: {e}")
        finally:
            await neo4j_client.close()

        return extraction

vision_agent = VisionAgent()
