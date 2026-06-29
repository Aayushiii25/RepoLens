import { cn } from "@/lib/utils"

interface SearchTabsProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const tabs = ["All", "Repositories", "Issues", "Organizations", "Technologies"]

export function SearchTabs({ activeTab, setActiveTab }: SearchTabsProps) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 border-b overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={cn(
            "px-3 py-1 text-xs font-medium rounded-full transition-colors whitespace-nowrap",
            activeTab === tab
              ? "bg-primary text-primary-foreground"
              : "bg-muted/50 text-muted-foreground hover:bg-muted"
          )}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
