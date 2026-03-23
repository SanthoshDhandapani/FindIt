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
      <div className="product-grid">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="product-card skeleton-card">
            <div className="skeleton-image" />
            <div className="skeleton-info">
              <div className="skeleton-line skeleton-brand" />
              <div className="skeleton-line skeleton-name" />
              <div className="skeleton-line skeleton-desc" />
              <div className="skeleton-line skeleton-price" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="grid-status grid-error">
        <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <p className="status-title">Something went wrong</p>
        <p className="status-desc">{error}</p>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="grid-status">
        <svg className="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          <line x1="8" y1="11" x2="14" y2="11" />
        </svg>
        <p className="status-title">No results found</p>
        <p className="status-desc">Try adjusting your search terms or filters</p>
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
