from app.models.schemas import Product


# ---------------------------------------------------------------------------
# Embedding service using all-MiniLM-L6-v2 via sentence-transformers
# Model: sentence-transformers/all-MiniLM-L6-v2 (384 dims, 256 max tokens, ~80MB)
# ---------------------------------------------------------------------------

def embed_text(text: str) -> list[float]:
    # TODO: Load SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") as lazy singleton
    # TODO: Encode text and return 384-dim vector
    # Use model.encode(text) → list[float]
    raise NotImplementedError


def embed_batch(texts: list[str]) -> list[list[float]]:
    # TODO: Batch encode multiple texts using same singleton model
    # More efficient than calling embed_text in a loop
    # Use model.encode(texts) → list[list[float]]
    raise NotImplementedError


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
