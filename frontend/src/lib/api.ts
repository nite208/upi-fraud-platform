// ── FraudShield API Client ─────────────────────────────────────────────────
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

// ── Transactions ───────────────────────────────────────────────────────────
export const submitTransaction = (txn: object) =>
  request('/transactions', { method: 'POST', body: JSON.stringify(txn) })

export const listTransactions = (limit = 50, decision?: string) =>
  request(`/transactions?limit=${limit}${decision ? `&decision=${decision}` : ''}`)

// ── Cases ──────────────────────────────────────────────────────────────────
export const listCases = (status?: string) =>
  request(`/cases${status ? `?status=${status}` : ''}`)

export const getCase = (caseId: string) =>
  request(`/cases/${caseId}`)

export const submitDisposition = (caseId: string, body: object) =>
  request(`/cases/${caseId}/disposition`, { method: 'PATCH', body: JSON.stringify(body) })

// ── Investigation ──────────────────────────────────────────────────────────
export const explainTransaction = (txnId: string) =>
  request(`/investigate/explain/${txnId}`, { method: 'POST' })

export const askQuestion = (body: object) =>
  request('/investigate/ask', { method: 'POST', body: JSON.stringify(body) })

export const generateSAR = (caseId: string) =>
  request(`/investigate/sar/${caseId}`, { method: 'POST' })

// ── Graph ──────────────────────────────────────────────────────────────────
export const getAccountGraph = (vpa: string) =>
  request(`/graph/account/${encodeURIComponent(vpa)}`)

export const getMuleAccounts = () =>
  request('/graph/mules')

export const getFraudRings = () =>
  request('/graph/rings')

// ── Analytics ─────────────────────────────────────────────────────────────
export const getModelPerformance = () =>
  request('/analytics/model/performance')

export const getDashboardSummary = () =>
  request('/analytics/summary')

export const getHeatmap = () =>
  request('/analytics/heatmap')

// ── Health ─────────────────────────────────────────────────────────────────
export const checkHealth = () =>
  request<{ status: string }>('/health'.replace('/api/v1', ''))