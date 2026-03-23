import { useState, type FormEvent } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      onSearch(trimmed);
    }
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        className="search-input"
        placeholder="Search products… e.g. 'red running shoes under $100'"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        autoFocus
      />
      <button type="submit" className="search-button" disabled={loading}>
        {loading ? "Searching…" : "Search"}
      </button>
    </form>
  );
}
