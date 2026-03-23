interface FiltersProps {
  category: string;
  brand: string;
  color: string;
  priceMin: string;
  priceMax: string;
  onCategoryChange: (value: string) => void;
  onBrandChange: (value: string) => void;
  onColorChange: (value: string) => void;
  onPriceMinChange: (value: string) => void;
  onPriceMaxChange: (value: string) => void;
}

export function Filters({
  category,
  brand,
  color,
  priceMin,
  priceMax,
  onCategoryChange,
  onBrandChange,
  onColorChange,
  onPriceMinChange,
  onPriceMaxChange,
}: FiltersProps) {
  return (
    <aside className="filters">
      <h3 className="filters-title">Filters</h3>

      <div className="filter-group">
        <label htmlFor="category">Category</label>
        <select
          id="category"
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="Electronics">Electronics</option>
          <option value="Clothes">Clothes</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="brand">Brand</label>
        <input
          id="brand"
          type="text"
          placeholder="e.g. Nike, Sony"
          value={brand}
          onChange={(e) => onBrandChange(e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="color">Color</label>
        <input
          id="color"
          type="text"
          placeholder="e.g. red, blue"
          value={color}
          onChange={(e) => onColorChange(e.target.value)}
        />
      </div>

      <div className="filter-group">
        <label>Price Range</label>
        <div className="price-range">
          <input
            type="number"
            placeholder="Min"
            min="0"
            value={priceMin}
            onChange={(e) => onPriceMinChange(e.target.value)}
          />
          <span className="price-separator">–</span>
          <input
            type="number"
            placeholder="Max"
            min="0"
            value={priceMax}
            onChange={(e) => onPriceMaxChange(e.target.value)}
          />
        </div>
      </div>
    </aside>
  );
}
