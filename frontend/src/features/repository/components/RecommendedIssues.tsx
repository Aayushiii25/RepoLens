"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"
import { Loader2 } from "lucide-react"

export function RecommendedIssues() {
  const { issues, isLoadingIssues } = useRepository()

  // Map API issues to display format, fall back to mock
  const displayIssues = issues.length > 0
    ? issues.map((issue) => ({
        id: `issue-${issue.number}`,
        title: issue.title,
        difficulty: issue.difficulty,
        estimatedTime: issue.difficulty === "Easy" ? "1-2 hours" : issue.difficulty === "Medium" ? "3-6 hours" : "1-3 days",
        labels: issue.labels.map(l => l.name),
        acceptanceRate: issue.difficulty === "Easy" ? "90%" : issue.difficulty === "Medium" ? "65%" : "35%",
        number: issue.number,
      }))
    : mockRepository.recommendedIssues

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">
        {issues.length > 0 ? "Open Issues" : "Recommended Issues"}
      </h3>
      {isLoadingIssues ? (
        <div className="flex items-center gap-2 text-muted-foreground py-8 justify-center">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Loading issues...</span>
        </div>
      ) : (
        <div className="border rounded-md overflow-hidden">
          <Table>
            <TableHeader className="bg-muted/30">
              <TableRow>
                <TableHead className="w-[40%]">Issue</TableHead>
                <TableHead>Difficulty</TableHead>
                <TableHead>Estimated Time</TableHead>
                <TableHead>Labels</TableHead>
                <TableHead>Acceptance</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayIssues.slice(0, 10).map((issue) => (
                <TableRow key={issue.id} className="cursor-pointer hover:bg-muted/10 transition-colors group">
                  <TableCell className="font-medium">{issue.title}</TableCell>
                  <TableCell>
                    <Badge variant={
                      issue.difficulty === "Easy" ? "default" :
                      issue.difficulty === "Medium" ? "secondary" : "destructive"
                    } className="font-normal bg-opacity-20">
                      {issue.difficulty}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">{issue.estimatedTime}</TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {issue.labels.slice(0, 3).map(label => (
                        <Badge key={label} variant="outline" className="text-xs text-muted-foreground">{label}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">{issue.acceptanceRate}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      Quick View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}
