import { GitCommit, GitPullRequest, CircleDot, Rocket } from "lucide-react"
import { mockRepository } from "@/data/repository"

export function RepositoryActivity() {
  const { recentActivity } = mockRepository

  const getIcon = (type: string) => {
    switch (type) {
      case "commit": return <GitCommit className="w-4 h-4 text-blue-500" />
      case "pull-request": return <GitPullRequest className="w-4 h-4 text-purple-500" />
      case "issue": return <CircleDot className="w-4 h-4 text-emerald-500" />
      case "release": return <Rocket className="w-4 h-4 text-orange-500" />
      default: return <GitCommit className="w-4 h-4" />
    }
  }

  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
      <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
        {recentActivity.map((activity) => (
          <div key={activity.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="flex items-center justify-center w-10 h-10 rounded-full border bg-background shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10">
              {getIcon(activity.type)}
            </div>
            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-card border rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-sm">{activity.title}</span>
              </div>
              <div className="text-xs text-muted-foreground flex items-center gap-2">
                <span>{activity.author}</span>
                <span>•</span>
                <span>{activity.date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
