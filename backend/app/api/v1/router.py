from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

logger = logging.getLogger(__name__)

api_router = APIRouter()

class SynthetixPayload(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

def build_and_run_pipeline(nodes: List[dict], edges: List[dict]) -> Dict[str, str]:
    """
    Takes a JSON graph, traces the execution path from Input -> Prompt -> LLM -> Output
    and returns the outputs for the Output nodes.
    """
    # 1. Build lookup tables
    node_map = {n["id"]: n for n in nodes}
    
    # 2. Find Output nodes
    output_nodes = [n for n in nodes if n["type"] == "outputNode"]
    results = {}
    
    # LLM Initialization
    llm = ChatGroq(
        temperature=0.7, 
        groq_api_key=settings.GROQ_API_KEY, 
        model_name="llama-3.1-8b-instant"
    )
    
    # Helper to find source node of an edge
    def get_source_node(target_id: str):
        for e in edges:
            if e["target"] == target_id:
                return node_map.get(e["source"])
        return None

    # Helper to find all source nodes connected to a target
    def get_source_nodes(target_id: str):
        sources = []
        for e in edges:
            if e["target"] == target_id:
                n = node_map.get(e["source"])
                if n:
                    sources.append(n)
        return sources

    for out_node in output_nodes:
        # Trace back from Output -> LLM
        llm_node = get_source_node(out_node["id"])
        if not llm_node or llm_node["type"] != "llmNode":
            results[out_node["id"]] = "Error: Output must be connected to an LLM node."
            continue
            
        # Trace back from LLM -> Inputs & Prompts
        llm_sources = get_source_nodes(llm_node["id"])
        
        system_prompt = "You are a helpful AI assistant."
        user_input = ""
        
        for src in llm_sources:
            if src["type"] == "promptNode":
                system_prompt = src.get("data", {}).get("value", system_prompt)
            elif src["type"] == "inputNode":
                user_input = src.get("data", {}).get("value", user_input)
                
        if not user_input:
            results[out_node["id"]] = "Error: No user input connected to LLM."
            continue
            
        try:
            # Dynamically execute LangChain
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            chain = prompt_template | llm
            response = chain.invoke({"input": user_input})
            
            results[out_node["id"]] = response.content
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}")
            results[out_node["id"]] = f"LLM Execution Error: {str(e)}"
            
    return results

@api_router.post("/execute")
async def execute_pipeline(payload: SynthetixPayload):
    try:
        outputs = build_and_run_pipeline(payload.nodes, payload.edges)
        return {"status": "success", "outputs": outputs}
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
