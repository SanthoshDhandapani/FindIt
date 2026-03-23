from pydantic import BaseModel
from typing import Literal, Optional


class SearchRequest(BaseModel):
    query: str
    category: Optional[Literal["electronics", "shoes", "stationery"]] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort_by: Literal["relevancy", "rating", "price_asc", "price_desc"] = "relevancy"
    top_k: int = 10


class ProductResult(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    color: Optional[str]
    price: float
    rating: float
    review_count: int
    relevancy_score: float
    image_url: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: list[ProductResult]
    total: int
    search_mode: str  # "semantic" | "keyword" | "hybrid"
    alpha: float
    latency_ms: float


class ParsedIntent(BaseModel):
    """Structured output from the Query Analyst agent."""
    category: Optional[Literal["electronics", "shoes", "stationery"]] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort_by: Literal["relevancy", "rating", "price_asc", "price_desc"] = "relevancy"
    keywords: list[str] = []
    specificity: Literal["high", "medium", "low"] = "medium"


class Product(BaseModel):
    """Product catalog entry."""
    product_id: str
    name: str
    brand: str
    category: Literal["electronics", "shoes", "stationery"]
    subcategory: Optional[str] = None
    color: Optional[str] = None
    price: float
    rating: float
    review_count: int
    description: Optional[str] = None
    key_features: list[str] = []
    stock_status: Literal["in_stock", "out_of_stock", "low_stock"] = "in_stock"
    image_url: Optional[str] = None

    def to_embedding_text(self) -> str:
        """Compose the text field used for embedding generation."""
        parts = [
            self.brand,
            self.name,
            self.color or "",
            self.subcategory or self.category,
            " ".join(self.key_features),
            self.description or "",
        ]
        return " ".join(p for p in parts if p).strip()

    def to_pinecone_metadata(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "subcategory": self.subcategory or "",
            "color": self.color or "",
            "price": self.price,
            "rating": self.rating,
            "review_count": self.review_count,
            "stock_status": self.stock_status,
            "image_url": self.image_url or "",
        }
