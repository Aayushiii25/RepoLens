import { RepositorySummary } from "./RepositorySummary"
import { TechStack } from "./TechStack"
import { LearningOutcomes } from "./LearningOutcomes"
import { RecommendedIssues } from "./RecommendedIssues"
import { RepositoryActivity } from "./RepositoryActivity"

export function RepositoryOverview() {
  return (
    <div className="py-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <RepositorySummary />
      <TechStack />
      <LearningOutcomes />
      <RecommendedIssues />
      <RepositoryActivity />
    </div>
  )
}
