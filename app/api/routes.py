from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.models.schemas import SearchRequest, SearchResponse, Product
from app.services.search import hybrid_search
from app.services.ingestion import ingest_product, ingest_products_bulk
from app.services.embedding import delete_product

router = APIRouter()


@router.post("/search", response_model=SearchResponse, tags=["search"])
def search(request: SearchRequest) -> SearchResponse:
    return hybrid_search(request)


@router.post("/index", tags=["ingestion"])
def index_product(product: Product) -> dict:
    return ingest_product(product)


@router.post("/index/bulk", tags=["ingestion"])
def index_products_bulk_route(products: list[Product]) -> dict:
    return ingest_products_bulk(products)


@router.delete("/index/{product_id}", tags=["ingestion"])
def remove_product(product_id: str, category: str = Query(..., description="Product category (namespace)")) -> dict:
    delete_product(product_id, category)
    return {"product_id": product_id, "status": "deleted", "namespace": category}


@router.get("/health", tags=["observability"])
def health() -> dict:
    checks = {"status": "ok"}

    # Check Pinecone
    try:
        from app.db.clients import get_pinecone_index
        stats = get_pinecone_index().describe_index_stats()
        checks["pinecone"] = {"status": "connected", "total_vectors": stats["total_vector_count"]}
    except Exception as e:
        checks["pinecone"] = {"status": "error", "detail": str(e)}
        checks["status"] = "degraded"

    # Check Redis
    try:
        import redis
        from app.config import settings
        r = redis.from_url(settings.redis_url)
        r.ping()
        checks["redis"] = {"status": "connected"}
    except Exception as e:
        checks["redis"] = {"status": "error", "detail": str(e)}
        checks["status"] = "degraded"

    return checks
