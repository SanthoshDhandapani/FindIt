import type { ProductResult } from "@/types/api";
import { ProductCard } from "./ProductCard";

interface ProductGridProps {
  products: ProductResult[];
  loading: boolean;
  error: string | null;
}

export function ProductGrid({ products, loading, error }: ProductGridProps) {
  if (loading) {
    return (
      <div className="grid-status">
        <div className="spinner" />
        <p>Searching products…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="grid-status grid-error">
        <p>⚠ {error}</p>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="grid-status">
        <p>No results found. Try a different search.</p>
      </div>
    );
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <ProductCard key={product.product_id} product={product} />
      ))}
    </div>
  );
}
