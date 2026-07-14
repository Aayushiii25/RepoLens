"use client"

import { Badge } from "@/components/ui/badge"
import { useRepository } from "./RepositoryContext"
import { mockRepository } from "@/data/repository"

export function TechStack() {
  const { repo } = useRepository()

  // Use API languages if available, otherwise fall back to mock topics
  const techStack = repo?.languages && repo.languages.length > 0
    ? repo.languages.map(l => l.name)
    : repo?.topics && repo.topics.length > 0
      ? repo.topics
      : mockRepository.techStack

  const languages = repo?.languages || []

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Tech Stack</h3>
      {languages.length > 0 ? (
        <div className="space-y-3">
          {/* Language bar */}
          <div className="h-3 w-full rounded-full overflow-hidden flex">
            {languages.map((lang) => (
              <div
                key={lang.name}
                className="h-full transition-all duration-500"
                style={{
                  width: `${lang.percentage}%`,
                  backgroundColor: lang.color || "#6b7280",
                }}
                title={`${lang.name}: ${lang.percentage}%`}
              />
            ))}
          </div>
          {/* Language labels */}
          <div className="flex flex-wrap gap-2">
            {languages.map((lang) => (
              <Badge
                key={lang.name}
                variant="secondary"
                className="px-3 py-1 cursor-pointer hover:bg-secondary/80 transition-colors"
              >
                <span
                  className="w-2.5 h-2.5 rounded-full mr-1.5 inline-block"
                  style={{ backgroundColor: lang.color || "#6b7280" }}
                />
                {lang.name}
                <span className="text-muted-foreground ml-1.5">{lang.percentage}%</span>
              </Badge>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {techStack.map((tech) => (
            <Badge
              key={tech}
              variant="secondary"
              className="px-3 py-1 cursor-pointer hover:bg-secondary/80 transition-colors"
            >
              {tech}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}
