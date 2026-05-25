// frontend/types/index.ts
export interface Transaction {
  id: string
  date: string
  merchant: string
  rawDescription: string
  amount: number
  type: "debit" | "credit"
  category: Category
  confidence: number
  isAnomaly: boolean
  anomalyReason?: string
  manuallyUpdated: boolean
}

export type Category =
  | "Food" | "Transport" | "Groceries" | "Rent"
  | "EMI" | "Shopping" | "Investments" | "Other"

export interface CategoryStats {
  amount: number
  percentage: number
  transactionCount: number
}

export interface UploadResponse {
  statementId: string
  filename: string
  bankDetected: string
  totalTransactions: number
  transactions: Transaction[]
  summary: {
    totalDebit: number
    totalCredit: number
    byCategory: Record<Category, CategoryStats>
    anomalies: AnomalyAlert[]
    dailySpending: { date: string; amount: number }[]
  }
}

export interface AnomalyAlert {
  transactionId: string
  merchant: string
  amount: number
  reason: string
}

export interface Insight {
  type: "overspend" | "positive" | "suggestion" | "anomaly"
  category: Category
  title: string
  body: string
  severity: "success" | "warning" | "error" | "info"
}
