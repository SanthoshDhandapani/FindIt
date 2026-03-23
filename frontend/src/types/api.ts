export interface SearchRequest {
  query: string;
  category?: string;
  brand?: string;
  color?: string;
  price_min?: number;
  price_max?: number;
  sort_by: "relevancy" | "rating" | "price_asc" | "price_desc";
  top_k: number;
}

export interface ProductResult {
  product_id: string;
  name: string;
  brand: string;
  category: string;
  color: string | null;
  price: number;
  rating: number;
  review_count: number;
  relevancy_score: number;
  image_url: string | null;
}

export interface SearchResponse {
  query: string;
  results: ProductResult[];
  total: number;
  search_mode: string;
  alpha: number;
  latency_ms: number;
}
