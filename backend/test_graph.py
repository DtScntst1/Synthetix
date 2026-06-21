import asyncio
import logging
from app.agents.graph_builder import graph_builder_agent
from app.database.neo4j_client import neo4j_client

# Configure basic logging to see the output in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ingestion():
    # A sample text representing a corporate financial report
    sample_text = """
    On January 15, 2024, Acme Corp acquired GlobalTech for $500 Million. 
    Following the acquisition, Jane Doe was appointed as the new CEO of GlobalTech. 
    Acme Corp's revenue increased by 15% due to this strategic move.
    """
    
    doc_id = "DOC_FINANCIAL_001"
    page_number = 1
    
    logger.info("Starting Graph Extraction Test...")
    
    # Run the agent to process the text and insert into Neo4j Aura
    result = await graph_builder_agent.process_text_chunk(sample_text, doc_id, page_number)
    
    if result:
        logger.info("\n--- EXTRACTION SUCCESSFUL ---")
        logger.info(f"Extracted {len(result.nodes)} Nodes and {len(result.edges)} Edges.")
        
        print("\n[Extracted Nodes]")
        for node in result.nodes:
            print(f"- [{node.label}] {node.id} (Clearance: {node.clearance_level})")
            
        print("\n[Extracted Edges]")
        for edge in result.edges:
            print(f"- {edge.source_id} -[{edge.type}]-> {edge.target_id}")
            
        print("\n[Traceability]")
        print("Data successfully committed to Neo4j Aura Cloud!")
    else:
        logger.error("Extraction failed.")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_ingestion())
