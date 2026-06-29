import { SearchX } from "lucide-react"

interface EmptySearchProps {
  query: string
}

export function EmptySearch({ query }: EmptySearchProps) {
  if (!query) return null
  
  return (
    <div className="py-12 px-4 flex flex-col items-center justify-center text-center">
      <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
        <SearchX className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold mb-2">No repositories found</h3>
      <p className="text-sm text-muted-foreground max-w-sm mx-auto mb-6">
        We couldn't find anything matching "{query}". 
      </p>
      
      <div className="space-y-2 text-sm text-muted-foreground bg-muted/30 p-4 rounded-lg">
        <p className="font-medium text-foreground mb-2">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1 text-left">
          <li>Try searching for another language</li>
          <li>Remove any active filters</li>
          <li>Search broader terms</li>
        </ul>
      </div>
    </div>
  )
}
