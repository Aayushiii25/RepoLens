import { Star, GitFork, Copy, ExternalLink, BookmarkPlus, ArrowLeftRight, Clock, Scale } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { mockRepository } from "@/data/repository"

export function RepositoryHeader() {
  const repo = mockRepository

  return (
    <div className="flex flex-col gap-4 py-6 border-b">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold">{repo.owner} / {repo.name}</h1>
            <Badge variant="outline" className="ml-2 bg-muted/50">{repo.primaryLanguage}</Badge>
          </div>
          <p className="text-muted-foreground max-w-2xl text-sm">{repo.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <BookmarkPlus className="w-4 h-4 mr-2" /> Save
          </Button>
          <Button variant="outline" size="sm">
            <ArrowLeftRight className="w-4 h-4 mr-2" /> Compare
          </Button>
          <Button variant="outline" size="sm">
            <ExternalLink className="w-4 h-4 mr-2" /> GitHub
          </Button>
          <Button variant="ghost" size="icon">
            <Copy className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <Star className="w-4 h-4" />
          <span>{repo.stars.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <GitFork className="w-4 h-4" />
          <span>{repo.forks.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Scale className="w-4 h-4" />
          <span>{repo.license}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>Updated {repo.lastUpdated}</span>
        </div>
      </div>
    </div>
  )
}
