import type { ProductResult } from "@/types/api";

interface ProductCardProps {
  product: ProductResult;
}

function relevancyColor(score: number): string {
  if (score > 0.7) return "badge-green";
  if (score > 0.4) return "badge-yellow";
  return "badge-red";
}

function renderStars(rating: number) {
  const stars = [];
  const full = Math.floor(rating);
  const hasHalf = rating - full >= 0.25;

  for (let i = 0; i < 5; i++) {
    if (i < full) {
      stars.push(
        <svg key={i} className="star star-full" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      );
    } else if (i === full && hasHalf) {
      stars.push(
        <svg key={i} className="star star-half" viewBox="0 0 24 24">
          <defs>
            <linearGradient id={`half-${i}`}>
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="50%" stopColor="#e2e8f0" />
            </linearGradient>
          </defs>
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill={`url(#half-${i})`} />
        </svg>
      );
    } else {
      stars.push(
        <svg key={i} className="star star-empty" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      );
    }
  }
  return stars;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="product-card">
      <div className="product-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} loading="lazy" />
        ) : (
          <div className="image-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
          </div>
        )}
        <span className={`relevancy-badge ${relevancyColor(product.relevancy_score)}`}>
          {(product.relevancy_score * 100).toFixed(0)}%
        </span>
      </div>
      <div className="product-info">
        <div className="product-meta-top">
          <span className="product-brand">{product.brand}</span>
          {product.color && <span className="product-color-dot" title={product.color} />}
        </div>
        <h3 className="product-name">{product.name}</h3>
        <p className="product-description">{product.description}</p>
        <div className="product-price-row">
          <span className="product-price">
            &#8377;{product.price.toLocaleString("en-IN")}
          </span>
        </div>
        <div className="product-rating">
          <div className="stars-row">{renderStars(product.rating)}</div>
          <span className="rating-number">{product.rating.toFixed(1)}</span>
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
