"use client"

import React, { createContext, useContext, useState, useCallback, useEffect } from "react"
import {
  getRepository,
  getRepositoryIssues,
  getRepositoryActivity,
  getRepositorySummary,
  getRepositoryHealth,
  type RepositoryDetail,
  type IssueInfo,
  type CommitInfo,
  type RepositorySummary as RepositorySummaryType,
  type DetailedHealth,
} from "@/services/api"

interface RepositoryContextState {
  // Data
  repo: RepositoryDetail | null
  issues: IssueInfo[]
  activity: CommitInfo[]
  summary: RepositorySummaryType | null
  detailedHealth: DetailedHealth | null

  // Loading states
  isLoading: boolean
  isLoadingIssues: boolean
  isLoadingActivity: boolean
  isLoadingSummary: boolean
  isLoadingHealth: boolean

  // Error
  error: string | null

  // Actions
  loadRepository: (owner: string, name: string) => Promise<void>
  selectedRepo: { owner: string; name: string } | null
}

const RepositoryContext = createContext<RepositoryContextState | null>(null)

export function useRepository() {
  const ctx = useContext(RepositoryContext)
  if (!ctx) {
    throw new Error("useRepository must be used within a RepositoryProvider")
  }
  return ctx
}

export function RepositoryProvider({ children }: { children: React.ReactNode }) {
  const [repo, setRepo] = useState<RepositoryDetail | null>(null)
  const [issues, setIssues] = useState<IssueInfo[]>([])
  const [activity, setActivity] = useState<CommitInfo[]>([])
  const [summary, setSummary] = useState<RepositorySummaryType | null>(null)
  const [detailedHealth, setDetailedHealth] = useState<DetailedHealth | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingIssues, setIsLoadingIssues] = useState(false)
  const [isLoadingActivity, setIsLoadingActivity] = useState(false)
  const [isLoadingSummary, setIsLoadingSummary] = useState(false)
  const [isLoadingHealth, setIsLoadingHealth] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedRepo, setSelectedRepo] = useState<{ owner: string; name: string } | null>(null)

  const loadRepository = useCallback(async (owner: string, name: string) => {
    setIsLoading(true)
    setError(null)
    setSelectedRepo({ owner, name })

    try {
      // Load main repo data first
      const repoData = await getRepository(owner, name)
      setRepo(repoData)
      setIsLoading(false)

      // Load secondary data in parallel (non-blocking)
      setIsLoadingIssues(true)
      setIsLoadingActivity(true)
      setIsLoadingSummary(true)
      setIsLoadingHealth(true)

      const loadSecondary = async () => {
        try {
          const [issuesData, activityData, summaryData, healthData] = await Promise.allSettled([
            getRepositoryIssues(owner, name),
            getRepositoryActivity(owner, name),
            getRepositorySummary(owner, name),
            getRepositoryHealth(owner, name),
          ])

          if (issuesData.status === "fulfilled") setIssues(issuesData.value)
          if (activityData.status === "fulfilled") setActivity(activityData.value)
          if (summaryData.status === "fulfilled") setSummary(summaryData.value)
          if (healthData.status === "fulfilled") setDetailedHealth(healthData.value)
        } catch (e) {
          // Non-critical — individual errors are handled by Promise.allSettled
        } finally {
          setIsLoadingIssues(false)
          setIsLoadingActivity(false)
          setIsLoadingSummary(false)
          setIsLoadingHealth(false)
        }
      }

      loadSecondary()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load repository")
      setIsLoading(false)
    }
  }, [])

  return (
    <RepositoryContext.Provider
      value={{
        repo,
        issues,
        activity,
        summary,
        detailedHealth,
        isLoading,
        isLoadingIssues,
        isLoadingActivity,
        isLoadingSummary,
        isLoadingHealth,
        error,
        loadRepository,
        selectedRepo,
      }}
    >
      {children}
    </RepositoryContext.Provider>
  )
}
