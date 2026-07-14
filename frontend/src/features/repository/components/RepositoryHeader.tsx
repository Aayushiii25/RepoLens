"use client"

import { Star, GitFork, Copy, ExternalLink, BookmarkPlus, ArrowLeftRight, Clock, Scale, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"

export function RepositoryHeader() {
  const { repo, isLoading } = useRepository()

  // Fall back to mock data when no API data is available
  const data = repo
    ? {
        owner: repo.owner,
        name: repo.name,
        primaryLanguage: repo.language || "Unknown",
        description: repo.description || "",
        stars: repo.stars,
        forks: repo.forks,
        license: repo.license || "N/A",
        lastUpdated: repo.pushed_at
          ? new Date(repo.pushed_at).toLocaleDateString()
          : "Unknown",
        url: repo.url,
      }
    : {
        owner: mockRepository.owner,
        name: mockRepository.name,
        primaryLanguage: mockRepository.primaryLanguage,
        description: mockRepository.description,
        stars: mockRepository.stars,
        forks: mockRepository.forks,
        license: mockRepository.license,
        lastUpdated: mockRepository.lastUpdated,
        url: null,
      }

  return (
    <div className="flex flex-col gap-4 py-6 border-b">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                <span className="text-lg text-muted-foreground">Loading...</span>
              </div>
            ) : (
              <>
                <h1 className="text-2xl font-bold">{data.owner} / {data.name}</h1>
                <Badge variant="outline" className="ml-2 bg-muted/50">{data.primaryLanguage}</Badge>
              </>
            )}
          </div>
          <p className="text-muted-foreground max-w-2xl text-sm">{data.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <BookmarkPlus className="w-4 h-4 mr-2" /> Save
          </Button>
          <Button variant="outline" size="sm">
            <ArrowLeftRight className="w-4 h-4 mr-2" /> Compare
          </Button>
          {data.url && (
            <Button variant="outline" size="sm" asChild>
              <a href={data.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-2" /> GitHub
              </a>
            </Button>
          )}
          {!data.url && (
            <Button variant="outline" size="sm">
              <ExternalLink className="w-4 h-4 mr-2" /> GitHub
            </Button>
          )}
          <Button variant="ghost" size="icon">
            <Copy className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <Star className="w-4 h-4" />
          <span>{data.stars.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <GitFork className="w-4 h-4" />
          <span>{data.forks.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Scale className="w-4 h-4" />
          <span>{data.license}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>Updated {data.lastUpdated}</span>
        </div>
      </div>
    </div>
  )
}
