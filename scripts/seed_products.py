"""
Seed script — loads product data from files/combined_products.json and ingests into Pinecone.
Run: python scripts/seed_products.py
"""

import json
from dotenv import load_dotenv

load_dotenv()

from app.models.schemas import Product
from app.services.ingestion import ingest_products_bulk


def load_products(path: str = "files/products.json") -> list[Product]:
    with open(path) as f:
        raw = json.load(f)

    products = []
    for item in raw:
        metadata = item.get("metadata", {})

        # Build key_features from metadata fields
        key_features = []
        for key in ["ram", "storage", "material", "type", "gender", "shoe_size"]:
            if key in metadata:
                key_features.append(f"{key}: {metadata[key]}")

        product = Product(
            product_id=item["productID"],
            name=item["name"],
            brand=item["brand"],
            category=item["category"].lower(),
            subcategory=item.get("subCategory"),
            color=item.get("color"),
            price=item["price"],
            rating=float(metadata.get("rating") or 0.0),
            description=item.get("description"),
            key_features=key_features,
            image_url=item.get("image_url"),
        )
        products.append(product)

    return products


if __name__ == "__main__":
    products = load_products()
    print(f"Loaded {len(products)} products")

    # Show category breakdown
    cats = {}
    for p in products:
        cats[p.category] = cats.get(p.category, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    print("\nIngesting into Pinecone...")
    result = ingest_products_bulk(products)
    print(f"Done: {result}")
