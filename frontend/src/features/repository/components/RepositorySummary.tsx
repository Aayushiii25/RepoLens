"use client"

import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"
import { Loader2 } from "lucide-react"

export function RepositorySummary() {
  const { summary, isLoadingSummary } = useRepository()

  const architecture = summary?.architecture || mockRepository.architectureOverview

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Architecture Overview</h3>
      {isLoadingSummary ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Generating AI summary...</span>
        </div>
      ) : (
        <p className="text-muted-foreground leading-relaxed">
          {architecture}
        </p>
      )}
      {summary?.summary && (
        <p className="text-muted-foreground leading-relaxed mt-3">
          {summary.summary}
        </p>
      )}
    </div>
  )
}
