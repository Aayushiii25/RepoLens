"use client"

import * as React from "react"
import { Navbar } from "./Navbar"
import { Sidebar } from "./Sidebar"
import { CommandMenu } from "./CommandMenu"

interface AppShellProps {
  children: React.ReactNode
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop & Tablet Sidebar */}
        <div className="hidden md:block w-64 lg:w-72 border-r shrink-0">
          <Sidebar />
        </div>
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>

        {/* Right Panel - Hidden on Mobile/Tablet */}
        <aside className="hidden lg:block w-72 xl:w-80 border-l shrink-0 bg-muted/20">
          <div className="p-6">
            <h3 className="font-semibold text-lg mb-4">Repository Info</h3>
            <div className="space-y-4 text-sm text-muted-foreground">
              <p>Select a repository to view its details, AI insights, and activity.</p>
              {/* Placeholders for AI Assistant / Activity */}
              <div className="h-32 border border-dashed rounded-lg flex items-center justify-center">
                AI Assistant Placeholder
              </div>
            </div>
          </div>
        </aside>
      </div>
      <CommandMenu />
    </div>
  )
}
