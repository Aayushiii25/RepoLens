"use client"

import { AppShell } from "@/components/layout/AppShell"
import { PageContainer } from "@/components/layout/PageContainer"
import { RepositoryHeader } from "@/features/repository/components/RepositoryHeader"
import { RepositoryTabs } from "@/features/repository/components/RepositoryTabs"
import { RepositoryBreadcrumb } from "@/features/repository/components/RepositoryBreadcrumb"
import { RepositoryOverview } from "@/features/repository/components/RepositoryOverview"
import { RepositorySidebar } from "@/features/repository/components/RepositorySidebar"

export default function DashboardPage() {
  return (
    <AppShell rightPanel={<RepositorySidebar />}>
      <PageContainer>
        <div className="max-w-5xl mx-auto w-full">
          <RepositoryBreadcrumb />
          
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
  )
}
