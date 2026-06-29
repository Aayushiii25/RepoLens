import { mockRepository } from "@/data/repository"

export function RepositorySummary() {
  const { architectureOverview } = mockRepository

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Architecture Overview</h3>
      <p className="text-muted-foreground leading-relaxed">
        {architectureOverview}
      </p>
    </div>
  )
}
