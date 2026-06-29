import { BookOpen, CircleDot, Building2, Cpu } from "lucide-react"

interface SearchResultRowProps {
  result: any // In a real app, type this strictly
}

export function SearchResultRow({ result }: SearchResultRowProps) {
  const getIcon = () => {
    switch (result.type) {
      case "repository": return <BookOpen className="h-4 w-4 text-blue-500 mt-1" />
      case "issue": return <CircleDot className="h-4 w-4 text-emerald-500 mt-1" />
      case "organization": return <Building2 className="h-4 w-4 text-orange-500 mt-1" />
      case "technology": return <Cpu className="h-4 w-4 text-purple-500 mt-1" />
      default: return <BookOpen className="h-4 w-4 mt-1" />
    }
  }

  return (
    <div className="flex gap-3 w-full">
      <div className="shrink-0">
        {getIcon()}
      </div>
      <div className="flex flex-col flex-1 overflow-hidden">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium text-sm truncate">{result.title}</span>
          {result.status === "open" && (
            <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-1.5 py-0.5 rounded font-medium">OPEN</span>
          )}
        </div>
        
        {result.description && (
          <span className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
            {result.description}
          </span>
        )}
        
        {result.language && (
          <div className="flex items-center gap-1.5 mt-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-[10px] text-muted-foreground font-medium">{result.language}</span>
          </div>
        )}
      </div>
    </div>
  )
}
