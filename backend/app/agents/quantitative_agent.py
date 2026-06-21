import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.database.schema import GraphNode, GraphEdge
from app.database.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

class QuantitativeStat(BaseModel):
    """
    Detailed statistical metric extracted from a text or table.
    """
    id: str = Field(description="Unique ID for the statistic, e.g., 'STAT_GDP_GROWTH'")
    metric_name: str = Field(description="Name of the metric, e.g., 'Correlation Coefficient', 'GDP Growth'")
    value: float = Field(description="The numerical value extracted")
    unit: str = Field(description="The unit of measurement, e.g., '%', 'USD', 'Coefficient'")
    p_value: Optional[float] = Field(None, description="The statistical significance p-value, if reported")
    confidence_interval: Optional[str] = Field(None, description="The confidence interval, if reported")
    is_significant: bool = Field(False, description="True if p_value < 0.05 or explicitly stated as significant")

class QuantitativeExtraction(BaseModel):
    """
    Output schema for the Quantitative Agent.
    """
    stats: List[QuantitativeStat] = Field(description="List of statistical metrics extracted")
    related_entities: List[GraphNode] = Field(description="The business/economic entities related to these stats")
    edges: List[GraphEdge] = Field(description="Relationships linking the entities to the stats. Edge type should be 'HAS_STATISTIC' or 'CORRELATED_WITH'")

class QuantitativeAgent:
    def __init__(self):
        # We use strict structured output to force the LLM to output math/stats accurately
        self.llm = ChatGroq(
            temperature=0,  # Zero temperature for strictly analytical tasks
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192"
        ).with_structured_output(QuantitativeExtraction)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a rigorous Quantitative Data Scientist Agent. "
             "Your job is to read academic reports, regression tables, and financial statements. "
             "You must extract specific statistical indicators (estimators, correlation coefficients, p-values). "
             "Rules:\n"
             "1. If a p-value is mentioned (e.g., p < 0.01), record it. If p < 0.05, mark is_significant=True.\n"
             "2. Extract the actual mathematical value and unit.\n"
             "3. Extract the real-world entities (like 'R&D Spend', 'Global Trade') as GraphNodes.\n"
             "4. Connect the entities to the stat using GraphEdges (e.g., 'R&D_SPEND' -> 'CORRELATED_WITH' -> 'STAT_REVENUE_GROWTH')."
            ),
            ("human", "Document ID: {doc_id}\n\nReport Text / Table Data:\n{text}")
        ])

    async def process_quantitative_data(self, text: str, doc_id: str, page_number: int):
        logger.info(f"Quantitative Agent parsing statistics from {doc_id}...")
        
        chain = self.prompt | self.llm
        try:
            extraction: QuantitativeExtraction = await chain.ainvoke({
                "text": text,
                "doc_id": doc_id
            })
        except Exception as e:
            logger.error(f"Quantitative Extraction failed: {e}")
            return None

        await neo4j_client.connect()
        try:
            # 1. Insert the Entities
            for node in extraction.related_entities:
                node.source_document_id = doc_id
                node.source_page_number = page_number
                await neo4j_client.create_node(node)
                
            # 2. Insert the Statistics as Nodes with Label 'Statistic'
            for stat in extraction.stats:
                stat_node = GraphNode(
                    id=stat.id,
                    label="Statistic",
                    properties={
                        "metric_name": stat.metric_name,
                        "value": stat.value,
                        "unit": stat.unit,
                        "p_value": stat.p_value,
                        "confidence_interval": stat.confidence_interval,
                        "is_significant": stat.is_significant
                    },
                    source_document_id=doc_id,
                    source_page_number=page_number
                )
                await neo4j_client.create_node(stat_node)
                logger.info(f"Created Stat Node: {stat.id} (p-value: {stat.p_value}, Sig: {stat.is_significant})")

            # 3. Insert the Edges
            for edge in extraction.edges:
                await neo4j_client.create_edge(edge)
                logger.info(f"Created Math Edge: {edge.source_id} -[{edge.type}]-> {edge.target_id}")

        except Exception as e:
            logger.error(f"Quantitative Database insertion failed: {e}")
        finally:
            await neo4j_client.close()

        return extraction

quantitative_agent = QuantitativeAgent()
