interface SortBarProps {
  sortBy: string;
  onSortChange: (value: string) => void;
  resultCount: number;
  searchMode?: string;
  latencyMs?: number;
}

export function SortBar({
  sortBy,
  onSortChange,
  resultCount,
  searchMode,
  latencyMs,
}: SortBarProps) {
  return (
    <div className="sort-bar">
      <div className="result-info">
        <span className="result-count">{resultCount} results</span>
        {searchMode && (
          <span className="search-mode">Mode: {searchMode}</span>
        )}
        {latencyMs !== undefined && (
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
          <option value="price_asc">Price: Low → High</option>
          <option value="price_desc">Price: High → Low</option>
        </select>
      </div>
    </div>
  );
}
