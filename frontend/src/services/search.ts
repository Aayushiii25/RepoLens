const API_BASE = "http://localhost:8000/api/v1"

export interface RepositoryResult {
  id: number
  full_name: string
  owner: string
  name: string
  description: string | null
  language: string | null
  stars: number
  forks: number
  open_issues: number
  topics: string[]
  license: string | null
  default_branch: string | null
  updated_at: string | null
}

export interface SearchResponse {
  query: string
  count: number
  results: RepositoryResult[]
  cached: boolean
}

export async function searchRepositories(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`)

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`)
  }

  return response.json()
}
