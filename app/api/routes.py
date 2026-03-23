from fastapi import APIRouter
from fastapi.responses import Response

from app.models.schemas import SearchRequest, SearchResponse, Product

router = APIRouter()


@router.post("/search", response_model=SearchResponse, tags=["search"])
def search(request: SearchRequest) -> SearchResponse:
    # TODO: Call hybrid_search(request) and return SearchResponse
    raise NotImplementedError


@router.post("/index", tags=["ingestion"])
def index_product(product: Product) -> dict:
    # TODO: Call ingest_product(product) and return status dict
    raise NotImplementedError


@router.post("/index/bulk", tags=["ingestion"])
def index_products_bulk(products: list[Product]) -> dict:
    # TODO: Call ingest_products_bulk(products) and return summary dict
    raise NotImplementedError


@router.delete("/index/{product_id}", tags=["ingestion"])
def remove_product(product_id: str, category: str) -> dict:
    # TODO: Call delete_product(product_id, category) and return status
    raise NotImplementedError


@router.get("/metrics", tags=["observability"])
def metrics() -> Response:
    # TODO: Return Prometheus metrics via generate_latest()
    raise NotImplementedError


@router.get("/health", tags=["observability"])
def health() -> dict:
    # TODO: Return {"status": "ok"} with optional dependency checks
    return {"status": "ok"}
