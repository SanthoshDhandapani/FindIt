import type { SearchRequest, SearchResponse } from "@/types/api";
import { mockProducts } from "./mockData";

const USE_MOCK = true;
const API_BASE = "/api/v1";

export async function searchProducts(
  request: SearchRequest
): Promise<SearchResponse> {
  if (USE_MOCK) {
    return mockSearch(request);
  }

  const response = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Search failed (${response.status}): ${error}`);
  }

  return response.json();
}

function mockSearch(request: SearchRequest): Promise<SearchResponse> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        query: request.query,
        results: mockProducts,
        total: mockProducts.length,
        search_mode: "mock",
        alpha: 0.6,
        latency_ms: Math.random() * 50 + 10,
      });
    }, 300);
  });
}

export async function healthCheck(): Promise<{ status: string }> {
  if (USE_MOCK) return { status: "ok" };
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
