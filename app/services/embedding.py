from app.models.schemas import Product


# ---------------------------------------------------------------------------
# Phase 1 — OpenAI embedding functions
# ---------------------------------------------------------------------------

def embed_text(text: str) -> list[float]:
    # TODO: Call OpenAI text-embedding-3-small and return vector
    raise NotImplementedError


def embed_batch(texts: list[str]) -> list[list[float]]:
    # TODO: Batch embed multiple texts in one API call
    raise NotImplementedError


def upsert_product(product: Product) -> None:
    # TODO: Embed product and upsert to Pinecone (namespace = product.category)
    raise NotImplementedError


def upsert_products_batch(products: list[Product]) -> dict:
    # TODO: Batch embed and upsert products, grouped by category namespace
    # Returns: {"total": int, "upserted": int}
    raise NotImplementedError


def delete_product(product_id: str, category: str) -> None:
    # TODO: Delete product vector from Pinecone by ID and namespace
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Phase 3 — HuggingFace embedding fallback
# ---------------------------------------------------------------------------
# Pattern: Cost optimization
# Reference: Orchestration Frameworks/LlamaIndex/RAG_ChromaDB.ipynb
#
# Local embeddings using sentence-transformers for:
# - Development/testing (avoid OpenAI API costs)
# - Fallback when OpenAI API is down or rate-limited
# - Batch indexing large product catalogs
#
# Toggle via EMBEDDING_PROVIDER=openai|huggingface in .env
# Default model: all-MiniLM-L6-v2 (384 dims) — configure in app/config.py

def embed_text_local(text: str) -> list[float]:
    # TODO: Load sentence-transformers model (lazy singleton)
    # TODO: Encode text and return vector
    # Model: settings.hf_embedding_model (default: "all-MiniLM-L6-v2")
    raise NotImplementedError


def embed_batch_local(texts: list[str]) -> list[list[float]]:
    # TODO: Batch encode using sentence-transformers
    # More efficient than calling embed_text_local in a loop
    raise NotImplementedError


def get_embedding_fn():
    """Return the appropriate embedding function based on config.

    Returns embed_text if EMBEDDING_PROVIDER=openai (default),
    or embed_text_local if EMBEDDING_PROVIDER=huggingface.
    """
    # TODO: Read settings.embedding_provider
    # TODO: Return embed_text or embed_text_local accordingly
    raise NotImplementedError
