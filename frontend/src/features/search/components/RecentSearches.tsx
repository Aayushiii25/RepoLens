import { Clock, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface RecentSearchesProps {
  searches: string[]
  onSelect: (term: string) => void
  onRemove: (term: string) => void
  onClear: () => void
}

export function RecentSearches({ searches, onSelect, onRemove, onClear }: RecentSearchesProps) {
  return (
    <div className="mb-2">
      <div className="flex items-center justify-end px-2 mb-1">
        <Button variant="ghost" size="sm" onClick={onClear} className="h-6 text-xs text-muted-foreground hover:text-destructive">
          Clear All
        </Button>
      </div>
      {searches.map((term) => (
        <div 
          key={term} 
          className="flex items-center justify-between px-2 py-1.5 hover:bg-muted/50 rounded-md group"
        >
          <div 
            className="flex items-center gap-2 cursor-pointer flex-1"
            onClick={() => onSelect(term)}
          >
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">{term}</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
            onClick={(e) => {
              e.stopPropagation()
              onRemove(term)
            }}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ))}
    </div>
  )
}
