from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models.schemas import Product

# ---------------------------------------------------------------------------
# Embedding service using all-MiniLM-L6-v2 via sentence-transformers
# Model: sentence-transformers/all-MiniLM-L6-v2 (384 dims, 256 max tokens, ~80MB)
# ---------------------------------------------------------------------------

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> list[float]:
    model = _get_model()
    return model.encode(text).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts).tolist()


def upsert_product(product: Product) -> None:
    from app.db.clients import get_pinecone_index
    index = get_pinecone_index()
    vector = embed_text(product.to_embedding_text())
    index.upsert(
        vectors=[(product.product_id, vector, product.to_pinecone_metadata())],
        namespace=product.category,
    )


def upsert_products_batch(products: list[Product]) -> dict:
    from app.db.clients import get_pinecone_index
    index = get_pinecone_index()

    # Group by category (namespace)
    by_category: dict[str, list[Product]] = {}
    for p in products:
        by_category.setdefault(p.category, []).append(p)

    upserted = 0
    for category, cat_products in by_category.items():
        texts = [p.to_embedding_text() for p in cat_products]
        vectors = embed_batch(texts)
        records = [
            (p.product_id, vec, p.to_pinecone_metadata())
            for p, vec in zip(cat_products, vectors)
        ]
        # Upsert in batches of 100
        for i in range(0, len(records), 100):
            batch = records[i : i + 100]
            index.upsert(vectors=batch, namespace=category)
            upserted += len(batch)

    return {"total": len(products), "upserted": upserted}


def delete_product(product_id: str, category: str) -> None:
    from app.db.clients import get_pinecone_index
    index = get_pinecone_index()
    index.delete(ids=[product_id], namespace=category)
