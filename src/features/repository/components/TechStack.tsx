import { Badge } from "@/components/ui/badge"
import { mockRepository } from "@/data/repository"

export function TechStack() {
  const { techStack } = mockRepository

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Tech Stack</h3>
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
    </div>
  )
}
