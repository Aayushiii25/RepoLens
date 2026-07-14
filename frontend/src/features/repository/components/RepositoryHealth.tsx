"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"
import { TrendingUp, Minus, TrendingDown, Loader2 } from "lucide-react"

export function RepositoryHealth() {
  const { repo, detailedHealth, isLoadingHealth } = useRepository()

  // Use API health data if available, otherwise fall back to basic health from repo, then mock
  const health = repo?.health || mockRepository.health
  const detailed = detailedHealth

  const metrics = [
    { label: "Activity", score: health.activity },
    { label: "Security", score: health.security },
    { label: "Community", score: health.community },
    { label: "Documentation", score: health.documentation },
    { label: "Maintainability", score: health.maintainability },
  ]

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-emerald-500"
    if (score >= 60) return "bg-yellow-500"
    if (score >= 40) return "bg-orange-500"
    return "bg-red-500"
  }

  const getScoreTextColor = (score: number) => {
    if (score >= 80) return "text-emerald-500"
    if (score >= 60) return "text-yellow-500"
    if (score >= 40) return "text-orange-500"
    return "text-red-500"
  }

  const getLabel = (score: number) => {
    if (score >= 90) return "Excellent"
    if (score >= 75) return "Good"
    if (score >= 60) return "Fair"
    if (score >= 40) return "Needs Work"
    return "Critical"
  }

  const getTrendIcon = (key: string) => {
    if (!detailed) return null
    const dim = detailed.dimensions[key as keyof typeof detailed.dimensions]
    if (!dim) return null
    switch (dim.trend) {
      case "trending_up": return <TrendingUp className="w-3 h-3 text-emerald-500" />
      case "trending_down": return <TrendingDown className="w-3 h-3 text-red-500" />
      default: return <Minus className="w-3 h-3 text-muted-foreground" />
    }
  }

  return (
    <Card className="shadow-sm border-muted/60">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold flex items-center justify-between">
          <span>Repository Health</span>
          <span className={`text-3xl font-bold ${getScoreTextColor(health.overall)}`}>
            {isLoadingHealth ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              health.overall
            )}
          </span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">{getLabel(health.overall)}</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric) => {
            const dimKey = metric.label.toLowerCase()
            return (
              <div key={metric.label}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-muted-foreground flex items-center gap-1.5">
                    {metric.label}
                    {getTrendIcon(dimKey)}
                  </span>
                  <span className="font-medium">{metric.score}</span>
                </div>
                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getScoreColor(metric.score)} rounded-full transition-all duration-700 ease-out`}
                    style={{ width: `${metric.score}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Recommendations */}
        {detailed?.recommendations && detailed.recommendations.length > 0 && (
          <div className="mt-6 pt-4 border-t">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Recommendations</h4>
            <ul className="space-y-1.5">
              {detailed.recommendations.slice(0, 3).map((rec, i) => (
                <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                  <span className="text-amber-500 mt-0.5">•</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
