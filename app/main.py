from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="E-Commerce Search Engine",
    description="Multimodal product search using CrewAI agents + Pinecone hybrid retrieval",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")

# TODO: Add Redis cache middleware
# TODO: Add request latency middleware
# TODO: Add CORS middleware if needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
