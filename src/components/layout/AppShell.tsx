"use client"

import * as React from "react"
import { Navbar } from "./Navbar"
import { Sidebar } from "./Sidebar"
import { CommandMenu } from "./CommandMenu"

interface AppShellProps {
  children: React.ReactNode
  rightPanel?: React.ReactNode
}

export function AppShell({ children, rightPanel }: AppShellProps) {
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
        {rightPanel && (
          <aside className="hidden lg:block w-72 xl:w-80 border-l shrink-0 bg-muted/20 overflow-y-auto">
            {rightPanel}
          </aside>
        )}
      </div>
      <CommandMenu />
    </div>
  )
}
