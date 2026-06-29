"use client"

import * as React from "react"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import { trendingSearches } from "@/data/search"
import { searchRepositories, type RepositoryResult } from "@/services/search"
import { useRecentSearches } from "../hooks/useRecentSearches"
import { SearchTabs } from "./SearchTabs"
import { RecentSearches } from "./RecentSearches"
import { EmptySearch } from "./EmptySearch"
import { TrendingUp, BookOpen, Star, GitFork, Loader2 } from "lucide-react"

export function GlobalSearch() {
  const [open, setOpen] = React.useState(false)
  const [query, setQuery] = React.useState("")
  const [activeTab, setActiveTab] = React.useState("All")
  const [results, setResults] = React.useState<RepositoryResult[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const debounceRef = React.useRef<NodeJS.Timeout | null>(null)

  const { recentSearches, addSearch, removeSearch, clearSearches } = useRecentSearches()

  // Ctrl+K listener
  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  // Debounced search
  React.useEffect(() => {
    if (!query || query.trim().length < 2) {
      setResults([])
      setError(null)
      return
    }

    setIsLoading(true)
    setError(null)

    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(async () => {
      try {
        const response = await searchRepositories(query)
        setResults(response.results)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Search failed")
        setResults([])
      } finally {
        setIsLoading(false)
      }
    }, 400)

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [query])

  const handleSelect = (value: string) => {
    addSearch(value)
    setOpen(false)
    setQuery("")
    setResults([])
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput
        placeholder="Search repositories, issues or technologies..."
        value={query}
        onValueChange={setQuery}
      />
      <SearchTabs activeTab={activeTab} setActiveTab={setActiveTab} />
      <CommandList className="max-h-[60vh] overflow-y-auto p-2">
        <CommandEmpty>
          {isLoading ? (
            <SearchSkeleton />
          ) : error ? (
            <div className="py-8 text-center">
              <p className="text-sm text-destructive">{error}</p>
              <p className="text-xs text-muted-foreground mt-2">Check your connection or try again.</p>
            </div>
          ) : (
            <EmptySearch query={query} />
          )}
        </CommandEmpty>

        {/* Recent searches — shown when no query */}
        {!query && recentSearches.length > 0 && (
          <CommandGroup heading="Recent Searches">
            <RecentSearches
              searches={recentSearches}
              onSelect={setQuery}
              onRemove={removeSearch}
              onClear={clearSearches}
            />
          </CommandGroup>
        )}

        {/* Trending — shown when no query */}
        {!query && (
          <>
            {recentSearches.length > 0 && <CommandSeparator />}
            <CommandGroup heading="Trending Searches">
              {trendingSearches.map((term) => (
                <CommandItem key={term} onSelect={() => setQuery(term)} className="cursor-pointer">
                  <TrendingUp className="mr-2 h-4 w-4 text-muted-foreground" />
                  <span>{term}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        )}

        {/* Loading skeleton */}
        {query && isLoading && (
          <div className="px-2 py-4 space-y-3">
            <SearchSkeleton />
          </div>
        )}

        {/* Live results from GitHub */}
        {query && !isLoading && results.length > 0 && (
          <CommandGroup heading="Repositories">
            {results.map((repo) => (
              <CommandItem
                key={repo.id}
                onSelect={() => handleSelect(repo.full_name)}
                className="p-2 cursor-pointer"
              >
                <div className="flex gap-3 w-full">
                  <BookOpen className="h-4 w-4 text-blue-500 mt-1 shrink-0" />
                  <div className="flex flex-col flex-1 overflow-hidden">
                    <span className="font-medium text-sm truncate">{repo.full_name}</span>
                    {repo.description && (
                      <span className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                        {repo.description}
                      </span>
                    )}
                    <div className="flex items-center gap-3 mt-1.5 text-xs text-muted-foreground">
                      {repo.language && (
                        <span className="flex items-center gap-1">
                          <span className="w-2 h-2 rounded-full bg-blue-500" />
                          {repo.language}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        {repo.stars.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <GitFork className="w-3 h-3" />
                        {repo.forks.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  )
}


function SearchSkeleton() {
  return (
    <div className="space-y-3 py-2 animate-pulse">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex gap-3 px-2">
          <div className="w-4 h-4 bg-muted rounded mt-1 shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-muted rounded w-3/4" />
            <div className="h-3 bg-muted rounded w-full" />
            <div className="flex gap-3">
              <div className="h-3 bg-muted rounded w-16" />
              <div className="h-3 bg-muted rounded w-12" />
              <div className="h-3 bg-muted rounded w-12" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
