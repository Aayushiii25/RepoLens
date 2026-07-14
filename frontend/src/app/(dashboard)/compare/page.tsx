"use client"

import { AppShell } from "@/components/layout/AppShell"
import { PageContainer } from "@/components/layout/PageContainer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeftRight, Loader2, Plus, X, Star, GitFork } from "lucide-react"
import { useState } from "react"
import { compareRepositories, getRepository, type RepositoryDetail } from "@/services/api"

interface ComparisonResult {
  comparison: Array<{
    name: string
    strengths: string[]
    weaknesses: string[]
  }>
  recommendation: string
  winner: string
}

export default function ComparePage() {
  const [repoInputs, setRepoInputs] = useState(["", ""])
  const [repos, setRepos] = useState<RepositoryDetail[]>([])
  const [comparison, setComparison] = useState<ComparisonResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isComparing, setIsComparing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addRepo = () => {
    if (repoInputs.length < 5) {
      setRepoInputs([...repoInputs, ""])
    }
  }

  const removeRepo = (index: number) => {
    if (repoInputs.length > 2) {
      setRepoInputs(repoInputs.filter((_, i) => i !== index))
    }
  }

  const handleFetch = async () => {
    const validRepos = repoInputs.filter(r => r.includes("/"))
    if (validRepos.length < 2) {
      setError("Enter at least 2 repositories in owner/name format")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const repoData = await Promise.all(
        validRepos.map(r => {
          const [owner, name] = r.split("/")
          return getRepository(owner, name)
        })
      )
      setRepos(repoData)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch repositories")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCompare = async () => {
    const validRepos = repoInputs.filter(r => r.includes("/"))
    setIsComparing(true)
    try {
      const result = await compareRepositories(validRepos) as ComparisonResult
      setComparison(result)
    } catch (e) {
      setError("AI comparison failed")
    } finally {
      setIsComparing(false)
    }
  }

  return (
    <AppShell>
      <PageContainer>
        <div className="max-w-5xl mx-auto w-full">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <ArrowLeftRight className="w-6 h-6 text-purple-500" />
              <h1 className="text-2xl font-bold">Compare Repositories</h1>
            </div>
            <p className="text-muted-foreground">
              Side-by-side comparison of repositories with AI-powered analysis.
            </p>
          </div>

          {/* Input section */}
          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="space-y-3">
                {repoInputs.map((value, i) => (
                  <div key={i} className="flex gap-2 items-center">
                    <span className="text-xs font-bold text-muted-foreground w-6">#{i + 1}</span>
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => {
                        const updated = [...repoInputs]
                        updated[i] = e.target.value
                        setRepoInputs(updated)
                      }}
                      placeholder="owner/repository (e.g. facebook/react)"
                      className="flex-1 px-3 py-2 text-sm border rounded-md bg-background focus:ring-2 focus:ring-primary/30 focus:outline-none"
                    />
                    {repoInputs.length > 2 && (
                      <Button variant="ghost" size="icon" onClick={() => removeRepo(i)}>
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>

              <div className="flex gap-3 mt-4">
                {repoInputs.length < 5 && (
                  <Button variant="outline" size="sm" onClick={addRepo}>
                    <Plus className="w-4 h-4 mr-1" /> Add Repository
                  </Button>
                )}
                <Button onClick={handleFetch} disabled={isLoading}>
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Fetch & Compare
                </Button>
              </div>

              {error && (
                <p className="text-sm text-destructive mt-3">{error}</p>
              )}
            </CardContent>
          </Card>

          {/* Stats comparison table */}
          {repos.length >= 2 && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="text-lg">Statistics Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-2 text-muted-foreground font-medium">Metric</th>
                        {repos.map(r => (
                          <th key={r.full_name} className="text-center py-3 px-2 font-medium">{r.full_name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { label: "Stars", key: "stars", icon: <Star className="w-3 h-3 text-yellow-500" /> },
                        { label: "Forks", key: "forks", icon: <GitFork className="w-3 h-3" /> },
                        { label: "Language", key: "language", icon: null },
                        { label: "Open Issues", key: "open_issues", icon: null },
                        { label: "Health Score", key: "health_overall", icon: null },
                        { label: "License", key: "license", icon: null },
                        { label: "Contributors", key: "contributor_count", icon: null },
                      ].map(row => (
                        <tr key={row.label} className="border-b last:border-0">
                          <td className="py-3 px-2 text-muted-foreground flex items-center gap-1.5">
                            {row.icon} {row.label}
                          </td>
                          {repos.map(r => {
                            let value: string | number = ""
                            if (row.key === "health_overall") {
                              value = r.health?.overall || "N/A"
                            } else {
                              value = (r as Record<string, unknown>)[row.key] as string | number || "N/A"
                            }
                            if (typeof value === "number") value = value.toLocaleString()
                            return (
                              <td key={r.full_name} className="py-3 px-2 text-center font-medium">{value}</td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {!comparison && (
                  <div className="mt-4 pt-4 border-t text-center">
                    <Button onClick={handleCompare} disabled={isComparing}>
                      {isComparing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                      Generate AI Comparison
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* AI Comparison */}
          {comparison && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">AI Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {comparison.comparison?.map((repo) => (
                  <div key={repo.name} className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                      {repo.name}
                      {comparison.winner === repo.name && (
                        <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Winner</Badge>
                      )}
                    </h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs font-medium text-emerald-500 uppercase tracking-wider">Strengths</span>
                        <ul className="mt-1.5 space-y-1">
                          {repo.strengths?.map((s, i) => (
                            <li key={i} className="text-sm text-muted-foreground flex items-start gap-1.5">
                              <span className="text-emerald-500 mt-0.5">+</span> {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-red-500 uppercase tracking-wider">Weaknesses</span>
                        <ul className="mt-1.5 space-y-1">
                          {repo.weaknesses?.map((w, i) => (
                            <li key={i} className="text-sm text-muted-foreground flex items-start gap-1.5">
                              <span className="text-red-500 mt-0.5">−</span> {w}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}

                {comparison.recommendation && (
                  <div className="p-4 bg-muted/30 rounded-lg border">
                    <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Recommendation</span>
                    <p className="text-sm mt-1.5">{comparison.recommendation}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </PageContainer>
    </AppShell>
  )
}
