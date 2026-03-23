import type { ProductResult } from "@/types/api";
import rawProducts from "./products.json";

interface RawProduct {
  productID: string;
  name: string;
  color: string | null;
  brand: string;
  category: string;
  subCategory: string;
  description: string;
  price: number;
  image_url?: string;
  metadata: { rating: number | null };
}
  
export const mockProducts: ProductResult[] = (rawProducts as RawProduct[]).map(
  (p, i) => ({
    product_id: p.productID,
    name: p.name,
    brand: p.brand,
    category: p.category,
    sub_category: p.subCategory,
    color: p.color,
    description: p.description,
    price: p.price,
    rating: p.metadata.rating ?? 0,
    review_count: Math.floor(Math.random() * 10000) + 500,
    relevancy_score: Math.max(0.1, 1 - i * 0.01),
    image_url: p.image_url ?? ''
  })
);
