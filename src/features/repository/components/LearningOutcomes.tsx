import { CheckCircle2 } from "lucide-react"
import { mockRepository } from "@/data/repository"

export function LearningOutcomes() {
  const { learningOutcomes } = mockRepository

  return (
    <div className="mb-8 bg-muted/20 p-6 rounded-lg border">
      <h3 className="text-lg font-semibold mb-4">What you will learn</h3>
      <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {learningOutcomes.map((outcome, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
            <span className="text-sm text-foreground/90">{outcome}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
