interface SortBarProps {
  sortBy: string;
  onSortChange: (value: string) => void;
  resultCount: number;
  searchMode?: string;
  latencyMs?: number;
  hasSearched: boolean;
}

export function SortBar({
  sortBy,
  onSortChange,
  resultCount,
  searchMode,
  latencyMs,
  hasSearched,
}: SortBarProps) {
  return (
    <div className="sort-bar">
      <div className="result-info">
        <span className="result-count">
          {hasSearched
            ? `${resultCount} result${resultCount !== 1 ? "s" : ""}`
            : `${resultCount} products`}
        </span>
        {searchMode && searchMode !== "mock" && (
          <span className="search-mode">{searchMode}</span>
        )}
        {latencyMs !== undefined && hasSearched && (
          <span className="latency">{latencyMs.toFixed(0)}ms</span>
        )}
      </div>
      <div className="sort-control">
        <label htmlFor="sort">Sort by</label>
        <select
          id="sort"
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value)}
        >
          <option value="relevancy">Relevancy</option>
          <option value="rating">Rating</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
        </select>
      </div>
    </div>
  );
}
