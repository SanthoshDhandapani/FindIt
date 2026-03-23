import { useState, useEffect } from "react";
import { SearchBar } from "@/components/SearchBar";
import { SortBar } from "@/components/SortBar";
import { ProductGrid } from "@/components/ProductGrid";
import { useSearch } from "@/hooks/useSearch";
import type { SearchRequest } from "@/types/api";

const SUGGESTIONS = [
  "iPhone under ₹50,000",
  "Samsung Galaxy",
  "Gaming laptop RTX",
  "Redmi budget phone",
  "Apple premium",
  "HP laptop for students",
];

export function SearchPage() {
  const { response, loading, error, search, hasSearched } = useSearch();
  const [sortBy, setSortBy] = useState("relevancy");

  useEffect(() => {
    search({ query: "", sort_by: "relevancy", top_k: 20 });
  }, [search]);

  function handleSearch(query: string) {
    const request: SearchRequest = {
      query,
      sort_by: sortBy as SearchRequest["sort_by"],
      top_k: 20,
    };
    search(request);
  }

  function handleSuggestionClick(suggestion: string) {
    handleSearch(suggestion);
  }

  const showHero = !hasSearched;

  return (
    <div className="search-page">
      <header className="header">
        <h1 className="logo">
          <span className="logo-find">Find</span>
          <span className="logo-it">It</span>
        </h1>
        <SearchBar onSearch={handleSearch} loading={loading} />
      </header>

      {showHero && (
        <div className="hero">
          <p className="hero-subtitle">
            Discover the best products with AI-powered semantic search
          </p>
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="content">
        <main className="main">
          <SortBar
            sortBy={sortBy}
            onSortChange={setSortBy}
            resultCount={response?.total ?? 0}
            searchMode={response?.search_mode}
            latencyMs={response?.latency_ms}
            hasSearched={hasSearched}
          />
          <ProductGrid
            products={response?.results ?? []}
            loading={loading}
            error={error}
          />
        </main>
      </div>
    </div>
  );
}
