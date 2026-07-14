"use client"

import * as React from "react"
import { 
  LayoutDashboard, 
  Compass, 
  FolderGit2, 
  Bookmark, 
  TrendingUp, 
  GitCommit, 
  Settings,
  ArrowLeftRight,
  Brain,
} from "lucide-react"
import { SidebarItem } from "./SidebarItem"
import { SidebarSection } from "./SidebarSection"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

const navigation = [
  {
    title: "Overview",
    items: [
      { label: "Dashboard", href: "/", icon: LayoutDashboard },
      { label: "Discover", href: "/discover", icon: Compass },
    ]
  },
  {
    title: "Library",
    items: [
      { label: "Repositories", href: "/repositories", icon: FolderGit2 },
      { label: "Saved", href: "/saved", icon: Bookmark },
    ]
  },
  {
    title: "Insights",
    items: [
      { label: "Trending", href: "/trending", icon: TrendingUp },
      { label: "Compare", href: "/compare", icon: ArrowLeftRight },
      { label: "Contributions", href: "/contributions", icon: GitCommit },
    ]
  },
  {
    title: "AI Tools",
    items: [
      { label: "Smart Search", href: "/smart-search", icon: Brain },
    ]
  },
  {
    title: "Configuration",
    items: [
      { label: "Settings", href: "/settings", icon: Settings },
    ]
  }
]

export function Sidebar({ className }: { className?: string }) {
  return (
    <nav className={cn("flex flex-col h-full bg-background border-r", className)}>
      <ScrollArea className="flex-1 py-4">
        <div className="px-3 space-y-2">
          {navigation.map((section, idx) => (
            <SidebarSection key={idx} title={section.title}>
              {section.items.map((item) => (
                <SidebarItem 
                  key={item.href}
                  href={item.href}
                  icon={item.icon}
                  label={item.label}
                />
              ))}
            </SidebarSection>
          ))}
        </div>
      </ScrollArea>
    </nav>
  )
}
