/**
 * Unified API Client
 * 
 * Centralized API module for all backend endpoints.
 * All requests go through these functions, making it easy to:
 *   - Change base URL in one place
 *   - Add authentication headers
 *   - Handle errors consistently
 */

const API_BASE = "http://localhost:8000/api/v1"

// ── Types ──────────────────────────────────────────────────────

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

export interface LanguageInfo {
  name: string
  color: string | null
  percentage: number
}

export interface ContributorInfo {
  login: string
  avatar_url: string | null
  name: string | null
}

export interface ReleaseInfo {
  tag: string
  name: string
  published_at: string | null
  description: string | null
  is_latest: boolean
}

export interface LabelInfo {
  name: string
  color: string | null
}

export interface IssueInfo {
  number: number
  title: string
  body: string | null
  created_at: string | null
  author: string | null
  author_avatar: string | null
  labels: LabelInfo[]
  comment_count: number
  difficulty: string
}

export interface CommitInfo {
  message: string
  date: string | null
  author: string
  avatar: string | null
}

export interface HealthInfo {
  overall: number
  activity: number
  community: number
  documentation: number
  security: number
  maintainability: number
}

export interface RepositoryDetail {
  github_id: string
  full_name: string
  owner: string
  owner_avatar: string | null
  name: string
  description: string | null
  url: string | null
  homepage: string | null
  stars: number
  forks: number
  watchers: number
  language: string | null
  language_color: string | null
  languages: LanguageInfo[]
  topics: string[]
  open_issues: number
  closed_issues: number
  open_prs: number
  merged_prs: number
  commit_count: number
  license: string | null
  license_name: string | null
  default_branch: string | null
  created_at: string | null
  updated_at: string | null
  pushed_at: string | null
  health: HealthInfo
  contributors: ContributorInfo[]
  contributor_count: number
  releases: ReleaseInfo[]
  readme: string | null
  has_wiki: boolean
  has_issues: boolean
  has_code_of_conduct: boolean
  has_funding: boolean
  has_security_policy: boolean
}

export interface HealthDimension {
  score: number
  label: string
  trend: string
  factors: Record<string, unknown>
}

export interface DetailedHealth {
  overall: { score: number; label: string; trend: string }
  dimensions: {
    activity: HealthDimension
    community: HealthDimension
    documentation: HealthDimension
    security: HealthDimension
    maintainability: HealthDimension
  }
  recommendations: string[]
  metadata: { scored_at: string; version: string }
}

export interface RepositorySummary {
  summary: string
  architecture: string
  difficulty: string
  learning_outcomes: string[]
}

export interface TrendingRepo {
  full_name: string
  owner?: string
  name?: string
  description: string | null
  language: string | null
  stars: number
  forks: number
  topics: string[]
  updated_at?: string | null
}

export interface RepoRecommendation {
  repository: string
  score: number
  reason: string
  language: string | null
  stars: number
  topics: string[]
}

export interface IssueRecommendation {
  issue: number
  title: string
  difficulty: string
  estimatedTime: string
  score: number
  reason: string
}

// ── API Functions ──────────────────────────────────────────────

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`)
  }
  return response.json()
}

// Search
export async function searchRepositories(query: string): Promise<SearchResponse> {
  return apiGet<SearchResponse>(`/search?q=${encodeURIComponent(query)}`)
}

export async function semanticSearch(query: string, limit = 10) {
  return apiPost(`/search/semantic`, { query, limit })
}

// Repository
export async function getRepository(owner: string, name: string): Promise<RepositoryDetail> {
  return apiGet<RepositoryDetail>(`/repositories/${owner}/${name}`)
}

export async function getRepositoryHealth(owner: string, name: string): Promise<DetailedHealth> {
  return apiGet<DetailedHealth>(`/repositories/${owner}/${name}/health`)
}

export async function getRepositoryIssues(owner: string, name: string): Promise<IssueInfo[]> {
  return apiGet<IssueInfo[]>(`/repositories/${owner}/${name}/issues`)
}

export async function getRepositoryActivity(owner: string, name: string): Promise<CommitInfo[]> {
  return apiGet<CommitInfo[]>(`/repositories/${owner}/${name}/activity`)
}

export async function getRepositorySummary(owner: string, name: string): Promise<RepositorySummary> {
  return apiGet<RepositorySummary>(`/repositories/${owner}/${name}/summary`)
}

export async function getSimilarRepositories(owner: string, name: string, limit = 5) {
  return apiGet(`/repositories/${owner}/${name}/similar?limit=${limit}`)
}

// Analytics
export async function getTrendingRepositories(limit = 10): Promise<TrendingRepo[]> {
  return apiGet<TrendingRepo[]>(`/analytics/trending?limit=${limit}`)
}

export async function getLanguageTrends() {
  return apiGet(`/analytics/languages`)
}

export async function getTopicTrends() {
  return apiGet(`/analytics/topics`)
}

// Recommendations
export async function getRepoRecommendations(skills: string[]): Promise<RepoRecommendation[]> {
  return apiPost<RepoRecommendation[]>(`/recommendations/repositories`, { skills })
}

export async function getIssueRecommendations(skills: string[]): Promise<IssueRecommendation[]> {
  return apiPost<IssueRecommendation[]>(`/recommendations/issues`, { skills })
}

// AI
export async function explainRepository(owner: string, name: string) {
  return apiPost(`/ai/explain`, { owner, name })
}

export async function getContributionCoach(repoName: string, issueId: number, skills: string[]) {
  return apiPost(`/ai/contribution-coach`, {
    repo_name: repoName,
    issue_id: issueId,
    user_skills: skills,
  })
}

export async function compareRepositories(repoNames: string[]) {
  return apiPost(`/ai/repositories/compare`, { repo_names: repoNames })
}

export async function chatWithRepository(owner: string, name: string, message: string, history: object[] = []) {
  return apiPost(`/ai/repositories/${owner}/${name}/chat`, { message, history })
}
