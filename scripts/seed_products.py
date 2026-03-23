"""
Seed script — populates Pinecone with mock product data for all three categories.
Run: python scripts/seed_products.py
"""

from app.models.schemas import Product
from app.services.ingestion import ingest_products_bulk

MOCK_PRODUCTS: list[Product] = [
    # Electronics
    Product(product_id="elec-001", name="MacBook Pro 14", brand="Apple", category="electronics", subcategory="laptop", color="silver", price=1999.0, rating=4.8, review_count=3200, key_features=["M3 chip", "16GB RAM", "512GB SSD"]),
    Product(product_id="elec-002", name="Dell XPS 15", brand="Dell", category="electronics", subcategory="laptop", color="black", price=1499.0, rating=4.5, review_count=1800, key_features=["i7", "32GB RAM", "OLED display"]),
    Product(product_id="elec-003", name="LG UltraWide 34", brand="LG", category="electronics", subcategory="display", color="black", price=599.0, rating=4.6, review_count=940, key_features=["34 inch", "ultrawide", "curved", "4K"]),

    # Shoes
    Product(product_id="shoe-001", name="Air Max 270", brand="Nike", category="shoes", subcategory="running", color="red", price=150.0, rating=4.7, review_count=5400, key_features=["air cushion", "lightweight", "mesh upper"]),
    Product(product_id="shoe-002", name="Ultra Boost 22", brand="Adidas", category="shoes", subcategory="running", color="white", price=180.0, rating=4.8, review_count=4200, key_features=["boost foam", "primeknit", "responsive"]),
    Product(product_id="shoe-003", name="Classic Leather", brand="Reebok", category="shoes", subcategory="casual", color="white", price=80.0, rating=4.4, review_count=2100, key_features=["leather upper", "vintage", "comfortable"]),

    # Stationery
    Product(product_id="stat-001", name="Leuchtturm1917 A5", brand="Leuchtturm", category="stationery", subcategory="notebook", color="navy", price=22.0, rating=4.9, review_count=8700, key_features=["dotted", "hardcover", "numbered pages"]),
    Product(product_id="stat-002", name="Hydro Flask 32oz", brand="HydroFlask", category="stationery", subcategory="water_bottle", color="black", price=45.0, rating=4.8, review_count=12000, key_features=["insulated", "stainless steel", "leak proof"]),
    Product(product_id="stat-003", name="Staedtler Mars 925", brand="Staedtler", category="stationery", subcategory="pencil", color="silver", price=12.0, rating=4.7, review_count=3300, key_features=["mechanical", "0.5mm", "drafting"]),
]


if __name__ == "__main__":
    print(f"Seeding {len(MOCK_PRODUCTS)} products...")
    result = ingest_products_bulk(MOCK_PRODUCTS)
    print(f"Done: {result}")
