import { ChevronRight } from "lucide-react"

export function RepositoryBreadcrumb() {
  return (
    <div className="flex items-center text-sm text-muted-foreground mb-4">
      <span className="hover:text-foreground cursor-pointer transition-colors">Repositories</span>
      <ChevronRight className="w-4 h-4 mx-1 opacity-50" />
      <span className="hover:text-foreground cursor-pointer transition-colors">facebook</span>
      <ChevronRight className="w-4 h-4 mx-1 opacity-50" />
      <span className="text-foreground font-medium">react</span>
    </div>
  )
}
