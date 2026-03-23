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
    # TODO: Embed product using product.to_embedding_text() and upsert to Pinecone
    # Namespace = product.category
    raise NotImplementedError


def upsert_products_batch(products: list[Product]) -> dict:
    # TODO: Batch embed and upsert products, grouped by category namespace
    # Returns: {"total": int, "upserted": int}
    raise NotImplementedError


def delete_product(product_id: str, category: str) -> None:
    # TODO: Delete product vector from Pinecone by ID and namespace
    raise NotImplementedError
