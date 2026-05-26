// frontend/lib/api.ts
import axios, { isAxiosError } from "axios"
import type { Transaction } from "@/types"

/**
 * Always call same-origin `/api/*`.
 * Next.js (rewrites) routes those calls to the backend, avoiding CORS/preflight issues.
 */
const api = axios.create({
  timeout: 120000,
})

export function getApiErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const data = error.response?.data as { message?: string; error?: string } | undefined
    if (data?.message) {
      return data.message
    }
    if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
      return (
        "Cannot reach the backend. Make sure it is running on port 8000 " +
        "(cd ml-engine, then: python -m uvicorn main:app --reload --port 8000)."
      )
    }
    if (error.response?.status === 413) {
      return "File is too large. Maximum size is 10MB."
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Something went wrong. Please try again."
}

export function mapTransaction(raw: Record<string, unknown>): Transaction {
  return {
    id: String(raw.id),
    date: String(raw.date),
    merchant: String(raw.merchant ?? ""),
    rawDescription: String(raw.rawDescription ?? raw.raw_description ?? ""),
    amount: Number(raw.amount),
    type: raw.type as Transaction["type"],
    category: raw.category as Transaction["category"],
    confidence: Number(raw.confidence ?? 0),
    isAnomaly: Boolean(raw.isAnomaly ?? raw.is_anomaly),
    anomalyReason: (raw.anomalyReason ?? raw.anomaly_reason) as string | undefined,
    manuallyUpdated: Boolean(raw.manuallyUpdated ?? raw.manually_updated),
  }
}

export const uploadStatement = async (file: File) => {
  const form = new FormData()
  form.append("file", file)
  // Do not set Content-Type — axios must add the multipart boundary automatically.
  const { data } = await api.post("/api/upload", form)
  return data
}

export const getStats = async (statementId: string, period = "monthly") => {
  const { data } = await api.get("/api/stats", {
    params: { statement_id: statementId, period },
  })
  return data
}

export const getInsights = async (statementId: string, language = "en") => {
  const { data } = await api.get("/api/insights", {
    params: { statement_id: statementId, language },
  })
  return data
}

export const getTransactions = async (
  statementId: string,
  {
    category,
    search,
    page = 1,
    limit = 20,
  }: {
    category?: string
    search?: string
    page?: number
    limit?: number
  } = {}
) => {
  const { data } = await api.get("/api/transactions", {
    params: { statement_id: statementId, category, search, page, limit },
  })
  return {
    ...data,
    transactions: (data.transactions ?? []).map((item: Record<string, unknown>) =>
      mapTransaction(item)
    ),
  }
}

export const recategorize = async (transactionId: string, category: string) => {
  const { data } = await api.patch(`/api/transactions/${transactionId}/category`, {
    category,
  })
  return data
}

export const loadDemo = async () => {
  const { data } = await api.post("/api/demo")
  return data
}
