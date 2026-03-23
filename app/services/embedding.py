from app.models.schemas import Product


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
