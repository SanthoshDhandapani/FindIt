import { useState } from "react";
import { SearchBar } from "@/components/SearchBar";
import { Filters } from "@/components/Filters";
import { SortBar } from "@/components/SortBar";
import { ProductGrid } from "@/components/ProductGrid";
import { useSearch } from "@/hooks/useSearch";
import type { SearchRequest } from "@/types/api";

export function SearchPage() {
  const { response, loading, error, search } = useSearch();

  const [category, setCategory] = useState("");
  const [brand, setBrand] = useState("");
  const [color, setColor] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [sortBy, setSortBy] = useState("relevancy");

  function handleSearch(query: string) {
    const request: SearchRequest = {
      query,
      sort_by: sortBy as SearchRequest["sort_by"],
      top_k: 12,
    };
    if (category) request.category = category as SearchRequest["category"];
    if (brand.trim()) request.brand = brand.trim();
    if (color.trim()) request.color = color.trim();
    if (priceMin) request.price_min = Number(priceMin);
    if (priceMax) request.price_max = Number(priceMax);

    search(request);
  }

  return (
    <div className="search-page">
      <header className="header">
        <h1 className="logo">FindIt</h1>
        <SearchBar onSearch={handleSearch} loading={loading} />
      </header>

      <div className="content">
        

        <main className="main">
          <SortBar
            sortBy={sortBy}
            onSortChange={setSortBy}
            resultCount={response?.total ?? 0}
            searchMode={response?.search_mode}
            latencyMs={response?.latency_ms}
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
