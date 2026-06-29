import { useState, useEffect } from "react"

const RECENT_SEARCHES_KEY = "repolens_recent_searches"

export function useRecentSearches() {
  const [recentSearches, setRecentSearches] = useState<string[]>([])

  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
      if (stored) {
        setRecentSearches(JSON.parse(stored))
      }
    } catch (e) {
      console.error("Failed to load recent searches", e)
    }
  }, [])

  const addSearch = (term: string) => {
    if (!term.trim()) return
    const newSearches = [term, ...recentSearches.filter(s => s !== term)].slice(0, 10)
    setRecentSearches(newSearches)
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(newSearches))
  }

  const removeSearch = (term: string) => {
    const newSearches = recentSearches.filter(s => s !== term)
    setRecentSearches(newSearches)
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(newSearches))
  }

  const clearSearches = () => {
    setRecentSearches([])
    localStorage.removeItem(RECENT_SEARCHES_KEY)
  }

  return { recentSearches, addSearch, removeSearch, clearSearches }
}
