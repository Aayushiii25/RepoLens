"use client"

import { RepositoryHealth } from "./RepositoryHealth"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

export function RepositorySidebar() {
  const { repo, isLoading } = useRepository()

  const contributors = repo?.contributors && repo.contributors.length > 0
    ? repo.contributors.map((c, i) => ({
        id: `${i}`,
        username: c.login,
        avatarUrl: c.avatar_url || "",
      }))
    : mockRepository.contributors

  const releases = repo?.releases && repo.releases.length > 0
    ? repo.releases.map((r, i) => ({
        id: `rel-${i}`,
        version: r.tag,
        isLatest: r.is_latest,
        description: r.description || "",
      }))
    : mockRepository.releases

  return (
    <div className="p-6 space-y-6">
      <RepositoryHealth />

      <div className="space-y-4">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
          Top Contributors
          {repo?.contributor_count ? ` (${repo.contributor_count})` : ""}
        </h3>
        {isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="w-4 h-4 animate-spin" />
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {contributors.map((c) => (
              <Avatar key={c.id} className="w-8 h-8 border cursor-pointer hover:ring-2 hover:ring-primary transition-all">
                <AvatarImage src={c.avatarUrl} alt={c.username} />
                <AvatarFallback>{c.username[0]}</AvatarFallback>
              </Avatar>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">Recent Releases</h3>
        <div className="space-y-3">
          {releases.map((release) => (
            <div key={release.id} className="border rounded-md p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-sm">{release.version}</span>
                {release.isLatest && <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-full font-medium">LATEST</span>}
              </div>
              <p className="text-xs text-muted-foreground line-clamp-2">{release.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t">
        <Button className="w-full" variant="outline">View All Insights</Button>
      </div>
    </div>
  )
}
