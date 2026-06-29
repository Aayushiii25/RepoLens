import * as React from "react"
import { cn } from "@/lib/utils"

interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {}

export function PageContainer({ className, children, ...props }: PageContainerProps) {
  return (
    <div className={cn("container mx-auto p-4 md:p-6 lg:p-8", className)} {...props}>
      {children}
    </div>
  )
}
