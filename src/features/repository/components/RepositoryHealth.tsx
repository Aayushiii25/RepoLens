import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { mockRepository } from "@/data/repository"

export function RepositoryHealth() {
  const { health } = mockRepository

  const metrics = [
    { label: "Activity", score: health.activity },
    { label: "Security", score: health.security },
    { label: "Community", score: health.community },
    { label: "Documentation", score: health.documentation },
    { label: "Maintainability", score: health.maintainability },
  ]

  return (
    <Card className="shadow-sm border-muted/60">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold flex items-center justify-between">
          <span>Repository Health</span>
          <span className="text-3xl font-bold text-emerald-500">{health.overall}</span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">Excellent</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric) => (
            <div key={metric.label}>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-muted-foreground">{metric.label}</span>
                <span className="font-medium">{metric.score}</span>
              </div>
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-emerald-500 rounded-full" 
                  style={{ width: `${metric.score}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
