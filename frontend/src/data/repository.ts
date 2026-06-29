export const mockRepository = {
  id: "repo-1",
  name: "react",
  owner: "facebook",
  description: "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
  primaryLanguage: "TypeScript",
  stars: 215430,
  forks: 43210,
  license: "MIT",
  lastUpdated: "2 hours ago",
  health: {
    overall: 94,
    activity: 98,
    security: 95,
    community: 91,
    documentation: 89,
    maintainability: 93
  },
  techStack: ["TypeScript", "JavaScript", "React", "Jest", "Rollup", "Flow", "Yarn"],
  architectureOverview: "React utilizes a Virtual DOM architecture to optimize rendering. The core reconciler (Fiber) manages updates cooperatively. Hooks provide a functional API for state and side-effects, allowing composition without class overhead.",
  learningOutcomes: [
    "Understanding the Virtual DOM and reconciliation (Fiber)",
    "Mastering complex state management and Hooks internally",
    "Learning advanced patterns in monorepo management",
    "Gaining experience with large-scale open-source contribution"
  ],
  contributors: [
    { id: "1", username: "gaearon", role: "Maintainer", avatarUrl: "https://github.com/gaearon.png" },
    { id: "2", username: "sophiebits", role: "Maintainer", avatarUrl: "https://github.com/sophiebits.png" },
    { id: "3", username: "acdlite", role: "Maintainer", avatarUrl: "https://github.com/acdlite.png" },
    { id: "4", username: "sebmarkbage", role: "Maintainer", avatarUrl: "https://github.com/sebmarkbage.png" },
    { id: "5", username: "bvaughn", role: "Contributor", avatarUrl: "https://github.com/bvaughn.png" }
  ],
  recommendedIssues: [
    {
      id: "issue-1",
      title: "Bug: DevTools profiling incorrectly handles suspended components",
      difficulty: "Medium",
      estimatedTime: "3-4 hours",
      labels: ["Bug", "DevTools"],
      acceptanceRate: "78%"
    },
    {
      id: "issue-2",
      title: "Feature: Add support for custom Error Boundary fallback rendering",
      difficulty: "Hard",
      estimatedTime: "2-3 days",
      labels: ["Feature", "Core"],
      acceptanceRate: "45%"
    },
    {
      id: "issue-3",
      title: "Docs: Clarify behavior of useEffect cleanup function ordering",
      difficulty: "Easy",
      estimatedTime: "1 hour",
      labels: ["Documentation", "Good First Issue"],
      acceptanceRate: "95%"
    },
    {
      id: "issue-4",
      title: "Optimization: Reduce memory allocation during list reconciliation",
      difficulty: "Hard",
      estimatedTime: "1 week",
      labels: ["Performance", "Core"],
      acceptanceRate: "30%"
    },
    {
      id: "issue-5",
      title: "Chore: Update outdated dependencies in fixture workspace",
      difficulty: "Easy",
      estimatedTime: "30 mins",
      labels: ["Dependencies", "Good First Issue"],
      acceptanceRate: "99%"
    }
  ],
  recentActivity: [
    {
      id: "act-1",
      type: "commit",
      title: "Fix bug in concurrent rendering scheduler",
      author: "acdlite",
      date: "1 hour ago"
    },
    {
      id: "act-2",
      type: "pull-request",
      title: "Add comprehensive tests for new useFormState hook",
      author: "eps1lon",
      date: "3 hours ago"
    },
    {
      id: "act-3",
      type: "issue",
      title: "Hydration mismatch warning on SSR with custom elements",
      author: "gaearon",
      date: "Yesterday"
    },
    {
      id: "act-4",
      type: "release",
      title: "v18.3.0 released",
      author: "sebmarkbage",
      date: "2 days ago"
    }
  ],
  releases: [
    {
      id: "rel-1",
      version: "v18.3.0",
      date: "2 days ago",
      isLatest: true,
      description: "Minor release containing mostly bug fixes and preparation for React 19."
    },
    {
      id: "rel-2",
      version: "v18.2.0",
      date: "June 14, 2022",
      isLatest: false,
      description: "Stable release containing updates to concurrent rendering."
    }
  ]
}
