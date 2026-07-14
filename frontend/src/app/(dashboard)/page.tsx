"use client"

import { AppShell } from "@/components/layout/AppShell"
import { PageContainer } from "@/components/layout/PageContainer"
import { RepositoryHeader } from "@/features/repository/components/RepositoryHeader"
import { RepositoryTabs } from "@/features/repository/components/RepositoryTabs"
import { RepositoryBreadcrumb } from "@/features/repository/components/RepositoryBreadcrumb"
import { RepositoryOverview } from "@/features/repository/components/RepositoryOverview"
import { RepositorySidebar } from "@/features/repository/components/RepositorySidebar"
import { RepositoryProvider, useRepository } from "@/features/repository/components/RepositoryContext"
import { useEffect, useState } from "react"

function RepositoryLoader() {
  const { loadRepository, selectedRepo, error } = useRepository()
  const [input, setInput] = useState("")
  const [hasLoaded, setHasLoaded] = useState(false)

  // Load a default repository on mount
  useEffect(() => {
    if (!hasLoaded) {
      loadRepository("facebook", "react")
      setHasLoaded(true)
    }
  }, [hasLoaded, loadRepository])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const parts = input.trim().split("/")
    if (parts.length === 2) {
      loadRepository(parts[0], parts[1])
      setInput("")
    }
  }

  return (
    <>
      {/* Quick repository switcher */}
      <div className="mb-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Load repository (e.g. vercel/next.js)"
            className="flex-1 px-3 py-1.5 text-sm border rounded-md bg-background focus:ring-2 focus:ring-primary/30 focus:outline-none"
          />
          <button
            type="submit"
            className="px-4 py-1.5 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Load
          </button>
        </form>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md border border-destructive/20">
          {error}
        </div>
      )}
    </>
  )
}

export default function DashboardPage() {
  return (
    <RepositoryProvider>
      <AppShell rightPanel={<RepositorySidebar />}>
        <PageContainer>
          <div className="max-w-5xl mx-auto w-full">
            <RepositoryBreadcrumb />
            <RepositoryLoader />

            <div className="bg-card rounded-xl border shadow-sm overflow-hidden mb-6">
              <div className="px-6">
                <RepositoryHeader />
                <RepositoryTabs />
              </div>
            </div>

            <div className="px-1">
              <RepositoryOverview />
            </div>
          </div>
        </PageContainer>
      </AppShell>
    </RepositoryProvider>
  )
}
