from app.models.schemas import Product


def ingest_product(product: Product) -> dict:
    # TODO: Single product ingestion pipeline
    # Step 1 — product.to_embedding_text()   → composed text string
    # Step 2 — embed_text(text)              → 1536-dim vector
    # Step 3 — upsert to Pinecone            → namespace = product.category
    # Returns: {"product_id", "status", "namespace", "latency_ms", "indexed_at"}
    raise NotImplementedError


def ingest_products_bulk(products: list[Product]) -> dict:
    # TODO: Batch ingestion — use upsert_products_batch for efficiency
    # Returns: {"total", "upserted", "status", "latency_ms", "indexed_at"}
    raise NotImplementedError
