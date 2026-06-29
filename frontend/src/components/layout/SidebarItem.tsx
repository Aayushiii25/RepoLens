"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface SidebarItemProps {
  icon: LucideIcon
  label: string
  href: string
}

export function SidebarItem({ icon: Icon, label, href }: SidebarItemProps) {
  const pathname = usePathname()
  // Active state is true if pathname matches exactly, or if it's a subroute of a non-root route
  const isActive = pathname === href || (href !== '/' && pathname.startsWith(`${href}/`))

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        isActive
          ? "bg-secondary text-secondary-foreground"
          : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </Link>
  )
}
