import time
from datetime import datetime, timezone

from app.models.schemas import Product
from app.services.embedding import upsert_product, upsert_products_batch


def ingest_product(product: Product) -> dict:
    start = time.time()
    upsert_product(product)
    latency_ms = round((time.time() - start) * 1000, 1)
    return {
        "product_id": product.product_id,
        "status": "indexed",
        "namespace": product.category,
        "latency_ms": latency_ms,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }


def ingest_products_bulk(products: list[Product]) -> dict:
    start = time.time()
    result = upsert_products_batch(products)
    latency_ms = round((time.time() - start) * 1000, 1)
    return {
        "total": result["total"],
        "upserted": result["upserted"],
        "status": "complete",
        "latency_ms": latency_ms,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }
