from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

# Initialize FastAPI App
app = FastAPI(
    title="InsightGraph Enterprise API",
    description="Multi-Agent GraphRAG Backend powered by FastAPI, LangGraph, and Neo4j",
    version="1.0.0"
)

# Configure CORS for Frontend (Vercel/Localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Deployment için * yapıldı (Tüm sitelerden erişime açık)
    allow_credentials=False, # * ile kullanabilmek için False yapıldı
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "InsightGraph API is running"}
