import logging
from typing import Dict, TypedDict, Any, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.config import settings
from app.database.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. State Definition
# ---------------------------------------------------------
class AgentState(TypedDict):
    query: str
    user_clearance_level: int
    route: str  # e.g., 'quantitative', 'vision', 'general'
    context: str
    final_answer: str

# ---------------------------------------------------------
# 2. Router Logic
# ---------------------------------------------------------
class RouteDecision(BaseModel):
    route: str = Field(description="The chosen route: 'quantitative', 'vision', or 'general'")

def router_node(state: AgentState):
    """
    Decides which specialized path the query should take.
    """
    logger.info(f"Routing query: {state['query']}")
    llm = ChatGroq(
        temperature=0, 
        groq_api_key=settings.GROQ_API_KEY, 
        model_name="llama3-70b-8192"
    ).with_structured_output(RouteDecision)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a Router Agent. Analyze the user query and decide the route:\n"
         "- 'quantitative': if the query asks about statistics, math, regression, p-values, or exact numbers.\n"
         "- 'vision': if the query asks about charts, graphs, or visual trends.\n"
         "- 'general': for standard entity or relationship queries."
        ),
        ("human", "{query}")
    ])
    
    decision = (prompt | llm).invoke({"query": state["query"]})
    return {"route": decision.route}

# ---------------------------------------------------------
# 3. Graph Retriever (Handles Temporal & RBAC)
# ---------------------------------------------------------
async def graph_retriever_node(state: AgentState):
    """
    Retrieves data from Neo4j based on the route, respecting RBAC clearance.
    """
    logger.info(f"Retrieving data for route: {state['route']} with clearance {state['user_clearance_level']}")
    await neo4j_client.connect()
    
    try:
        # Simplified Temporal & RBAC Cypher Query
        # In a real app, we'd use vector search or full-text search here to find the entry point
        cypher_query = """
        MATCH (n)-[r]->(m)
        WHERE n.clearance_level <= $clearance AND m.clearance_level <= $clearance
        // Temporal logic: only active edges/nodes if valid_to is not expired
        AND (n.valid_to IS NULL OR n.valid_to > datetime())
        RETURN n.id, labels(n), type(r), m.id, labels(m) LIMIT 50
        """
        async with neo4j_client._driver.session() as session:
            result = await session.run(cypher_query, clearance=state["user_clearance_level"])
            records = await result.data()
            
        context_str = "\n".join([str(rec) for rec in records])
        return {"context": context_str}
    finally:
        await neo4j_client.close()

# ---------------------------------------------------------
# 4. Synthesizer Node
# ---------------------------------------------------------
def synthesizer_node(state: AgentState):
    """
    Takes the retrieved graph context and answers the user's query.
    """
    logger.info("Synthesizing final answer...")
    llm = ChatGroq(temperature=0.3, groq_api_key=settings.GROQ_API_KEY, model_name="llama3-70b-8192")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Enterprise AI Assistant. Use the provided Knowledge Graph Context to answer the user's query accurately. Do not hallucinate."),
        ("human", "Context:\n{context}\n\nQuery:\n{query}")
    ])
    
    response = (prompt | llm).invoke({"context": state["context"], "query": state["query"]})
    return {"final_answer": response.content}

# ---------------------------------------------------------
# 5. Graph Compilation
# ---------------------------------------------------------
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("graph_retriever", graph_retriever_node)
workflow.add_node("synthesizer", synthesizer_node)

# Add Edges
workflow.set_entry_point("router")
workflow.add_edge("router", "graph_retriever")
workflow.add_edge("graph_retriever", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the LangGraph App
orchestrator_app = workflow.compile()
