import { useState, useCallback } from "react";
import type { SearchRequest, SearchResponse } from "@/types/api";
import { searchProducts } from "@/services/api";

export function useSearch() {
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const search = useCallback(async (request: SearchRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchProducts(request);
      setResponse(data);
      if (request.query.trim()) setHasSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { response, loading, error, search, hasSearched };
}
