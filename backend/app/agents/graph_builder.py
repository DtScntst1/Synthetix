import logging
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.database.schema import GraphNode, GraphEdge
from app.database.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

class GraphExtraction(BaseModel):
    """
    The expected structured output from the LLM when extracting graph data.
    """
    nodes: List[GraphNode] = Field(description="List of entities extracted from the text.")
    edges: List[GraphEdge] = Field(description="List of relationships connecting the extracted entities.")

class GraphBuilderAgent:
    def __init__(self):
        # We use a highly capable model like Llama-3 (70B) via Groq for accurate structured parsing
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192"
        ).with_structured_output(GraphExtraction)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert Data Scientist and Knowledge Graph Architect. "
             "Your task is to read the provided text and extract entities (Nodes) and their relationships (Edges). "
             "Ensure you attach the correct temporal metadata (valid_from/to) if times are mentioned. "
             "If the text mentions sensitive company financials, set clearance_level to 2, otherwise 0. "
             "Nodes MUST have unique, uppercase IDs without spaces (e.g., 'APPLE_INC'). "
             "Edges MUST map exactly to the extracted Node IDs."
            ),
            ("human", "Document ID: {doc_id}\nPage: {page_number}\n\nText:\n{text}")
        ])

    async def process_text_chunk(self, text: str, doc_id: str, page_number: int):
        """
        Takes a chunk of text, asks the LLM to extract nodes and edges, 
        and inserts them directly into the Neo4j Graph Database.
        """
        logger.info(f"Processing chunk from Document {doc_id}, Page {page_number}")
        
        # 1. Run LangChain Extraction
        chain = self.prompt | self.llm
        try:
            extraction: GraphExtraction = await chain.ainvoke({
                "text": text,
                "doc_id": doc_id,
                "page_number": page_number
            })
        except Exception as e:
            logger.error(f"LLM Extraction failed: {e}")
            return None

        # 2. Add Traceability to Nodes
        for node in extraction.nodes:
            node.source_document_id = doc_id
            node.source_page_number = page_number

        # 3. Insert into Neo4j
        await neo4j_client.connect()
        try:
            # Insert Nodes
            for node in extraction.nodes:
                await neo4j_client.create_node(node)
                logger.info(f"Created Node: {node.id}")
                
            # Insert Edges
            for edge in extraction.edges:
                await neo4j_client.create_edge(edge)
                logger.info(f"Created Edge: {edge.source_id} -> {edge.target_id}")
                
        except Exception as e:
            logger.error(f"Database insertion failed: {e}")
        finally:
            await neo4j_client.close()

        return extraction

graph_builder_agent = GraphBuilderAgent()
