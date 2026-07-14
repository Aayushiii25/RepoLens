"use client"

import { CheckCircle2, Loader2 } from "lucide-react"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"

export function LearningOutcomes() {
  const { summary, isLoadingSummary } = useRepository()

  const learningOutcomes = summary?.learning_outcomes && summary.learning_outcomes.length > 0
    ? summary.learning_outcomes
    : mockRepository.learningOutcomes

  const difficulty = summary?.difficulty

  return (
    <div className="mb-8 bg-muted/20 p-6 rounded-lg border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">What you will learn</h3>
        {difficulty && (
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
            difficulty === "Beginner" ? "bg-emerald-500/10 text-emerald-500" :
            difficulty === "Intermediate" ? "bg-yellow-500/10 text-yellow-500" :
            "bg-red-500/10 text-red-500"
          }`}>
            {difficulty}
          </span>
        )}
      </div>
      {isLoadingSummary ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Analyzing learning outcomes...</span>
        </div>
      ) : (
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {learningOutcomes.map((outcome, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
              <span className="text-sm text-foreground/90">{outcome}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
