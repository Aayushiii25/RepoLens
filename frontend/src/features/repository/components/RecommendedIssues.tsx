import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { mockRepository } from "@/data/repository"

export function RecommendedIssues() {
  const { recommendedIssues } = mockRepository

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Recommended Issues</h3>
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
            {recommendedIssues.map((issue) => (
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
                    {issue.labels.map(label => (
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
    </div>
  )
}
