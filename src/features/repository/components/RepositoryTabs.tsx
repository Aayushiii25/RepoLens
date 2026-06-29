"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"

const tabs = ["Workspace", "Issues", "Pull Requests", "Contributors", "Analytics", "Releases"]

export function RepositoryTabs() {
  const [activeTab, setActiveTab] = useState("Workspace")

  return (
    <div className="w-full border-b overflow-x-auto">
      <nav className="flex items-center gap-6 px-1">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "py-4 text-sm font-medium transition-colors relative whitespace-nowrap",
              activeTab === tab
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {tab}
            {activeTab === tab && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-foreground rounded-t-full" />
            )}
          </button>
        ))}
      </nav>
    </div>
  )
}
