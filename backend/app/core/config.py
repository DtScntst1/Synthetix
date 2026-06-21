from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightGraph Enterprise API"
    
    # Neo4j Graph Database
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "insightgraph123")
    
    # PostgreSQL for RBAC
    POSTGRES_URI: str = os.getenv("POSTGRES_URI", "postgresql://admin:adminpassword@localhost:5432/insightgraph")
    
    # Groq / LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
