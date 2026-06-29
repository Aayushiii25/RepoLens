import * as React from "react"

interface SidebarSectionProps {
  title?: string
  children: React.ReactNode
}

export function SidebarSection({ title, children }: SidebarSectionProps) {
  return (
    <div className="flex flex-col gap-1 py-2">
      {title && (
        <h4 className="px-3 text-xs font-semibold text-muted-foreground tracking-wider uppercase mb-1">
          {title}
        </h4>
      )}
      {children}
    </div>
  )
}
