"use client"

import { AppShell } from "@/components/layout/AppShell"
import { PageContainer } from "@/components/layout/PageContainer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, GitFork, TrendingUp, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { getTrendingRepositories, type TrendingRepo } from "@/services/api"

export default function TrendingPage() {
  const [repos, setRepos] = useState<TrendingRepo[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getTrendingRepositories(15)
        setRepos(data)
      } catch {
        // Use empty state
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  return (
    <AppShell>
      <PageContainer>
        <div className="max-w-5xl mx-auto w-full">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-6 h-6 text-orange-500" />
              <h1 className="text-2xl font-bold">Trending Repositories</h1>
            </div>
            <p className="text-muted-foreground">
              Discover the most popular repositories based on star count and activity.
            </p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading trending repositories...</span>
            </div>
          ) : repos.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground">
              <p>No trending data available yet. Search for some repositories first!</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {repos.map((repo, i) => (
                <Card key={repo.full_name} className="hover:shadow-md transition-shadow cursor-pointer group">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1.5">
                          <span className="text-xs font-bold text-muted-foreground w-6">#{i + 1}</span>
                          <h3 className="font-semibold text-base group-hover:text-primary transition-colors">
                            {repo.full_name}
                          </h3>
                          {repo.language && (
                            <Badge variant="secondary" className="text-xs">{repo.language}</Badge>
                          )}
                        </div>
                        {repo.description && (
                          <p className="text-sm text-muted-foreground ml-9 line-clamp-2">{repo.description}</p>
                        )}
                        {repo.topics && repo.topics.length > 0 && (
                          <div className="flex gap-1.5 ml-9 mt-2 flex-wrap">
                            {repo.topics.slice(0, 5).map(topic => (
                              <Badge key={topic} variant="outline" className="text-xs">{topic}</Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground shrink-0">
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span className="font-medium">{repo.stars?.toLocaleString()}</span>
                        </div>
                        {repo.forks != null && (
                          <div className="flex items-center gap-1">
                            <GitFork className="w-4 h-4" />
                            <span>{repo.forks.toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </PageContainer>
    </AppShell>
  )
}
