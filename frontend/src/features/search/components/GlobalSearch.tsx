"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import { trendingSearches, mockSearchResults } from "@/data/search"
import { useRecentSearches } from "../hooks/useRecentSearches"
import { SearchResultRow } from "./SearchResultRow"
import { SearchTabs } from "./SearchTabs"
import { RecentSearches } from "./RecentSearches"
import { EmptySearch } from "./EmptySearch"
import { TrendingUp } from "lucide-react"

export function GlobalSearch() {
  const [open, setOpen] = React.useState(false)
  const [query, setQuery] = React.useState("")
  const [activeTab, setActiveTab] = React.useState("All")
  
  const { recentSearches, addSearch, removeSearch, clearSearches } = useRecentSearches()

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const handleSelect = (value: string) => {
    addSearch(value)
    setOpen(false)
    setQuery("")
  }

  // Filter results
  const filteredResults = query
    ? mockSearchResults.filter((item) => {
        const matchesQuery = item.title.toLowerCase().includes(query.toLowerCase()) || 
                             item.description?.toLowerCase().includes(query.toLowerCase())
        const matchesTab = activeTab === "All" || 
                           (activeTab === "Repositories" && item.type === "repository") ||
                           (activeTab === "Issues" && item.type === "issue") ||
                           (activeTab === "Organizations" && item.type === "organization") ||
                           (activeTab === "Technologies" && item.type === "technology")
        return matchesQuery && matchesTab
      })
    : []

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
          <EmptySearch query={query} />
        </CommandEmpty>

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

        {query && filteredResults.length > 0 && (
          <CommandGroup heading="Results">
            {filteredResults.map((result) => (
              <CommandItem 
                key={result.id} 
                onSelect={() => handleSelect(result.title)}
                className="p-2 cursor-pointer"
              >
                <SearchResultRow result={result} />
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  )
}
