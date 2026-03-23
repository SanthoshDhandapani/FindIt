import type { ProductResult } from "@/types/api";

interface ProductCardProps {
  product: ProductResult;
}

function relevancyColor(score: number): string {
  if (score > 0.7) return "badge-green";
  if (score > 0.4) return "badge-yellow";
  return "badge-red";
}

function renderStars(rating: number): string {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="product-card">
      <div className="product-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} loading="lazy" />
        ) : (
          <div className="image-placeholder">No Image</div>
        )}
        <span className={`relevancy-badge ${relevancyColor(product.relevancy_score)}`}>
          {product.relevancy_score.toFixed(2)}
        </span>
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-brand">{product.brand}</p>
        <p className="product-description">{product.description}</p>
        <p className="product-price">&#8377;{product.price.toLocaleString("en-IN")}</p>
        <div className="product-rating">
          <span className="stars">{renderStars(product.rating)}</span>
          <span className="review-count">({product.review_count.toLocaleString()})</span>
        </div>
        <div className="product-tags">
          <span className="product-category">{product.sub_category}</span>
          {product.color && (
            <span className="product-color">{product.color}</span>
          )}
        </div>
      </div>
    </div>
  );
}
