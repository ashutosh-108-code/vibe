"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { getStats, getTransactions } from "@/lib/api"
import { EmptyState } from "@/components/EmptyState"
import { SpendingDonut } from "@/components/SpendingDonut"
import { DailyBarChart } from "@/components/DailyBarChart"
import { TransactionTable } from "@/components/TransactionTable"
import { formatINR, formatDate } from "@/lib/formatters"
import { CATEGORY_CONFIG } from "@/lib/categories"
import type { Category, Transaction } from "@/types"
import { ArrowUpRight, ArrowDownRight, Wallet, Info, RefreshCw } from "lucide-react"

function DashboardContent() {
  const searchParams = useSearchParams()
  const statementId = searchParams.get("statement_id")
  const router = useRouter()

  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [error, setError] = useState("")

  const fetchData = async () => {
    if (!statementId) return
    setLoading(true)
    setError("")
    try {
      const statsData = await getStats(statementId)
      setStats(statsData)

      const txData = await getTransactions(statementId, { limit: 100 })
      setTransactions(txData.transactions || [])
    } catch (err) {
      console.error(err)
      setError("Could not load dashboard data. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (statementId) {
      fetchData()
    } else {
      setLoading(false)
    }
  }, [statementId])

  if (!statementId) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <EmptyState />
      </div>
    )
  }

  if (loading) {
    return <DashboardSkeleton />
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-800 shadow-sm">
          <Info className="mx-auto h-12 w-12 text-[#EF4444] mb-3" />
          <h2 className="text-xl font-semibold">Error Loading Data</h2>
          <p className="mt-2 text-sm">{error}</p>
          <div className="mt-4 flex justify-center gap-3">
            <button
              onClick={() => fetchData()}
              className="inline-flex items-center gap-2 rounded-lg bg-[#1E293B] px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
            >
              <RefreshCw className="h-4 w-4" /> Retry
            </button>
            <button
              onClick={() => router.push("/upload")}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Go to Upload
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Map category data for donut chart
  const donutData = Object.keys(CATEGORY_CONFIG).map((categoryName) => {
    const cat = categoryName as Category
    const catStats = stats?.by_category?.[cat]
    const amount = catStats ? catStats.amount : 0
    return {
      name: cat,
      amount: amount,
      color: CATEGORY_CONFIG[cat].color,
    }
  }).filter((item) => item.amount > 0)

  // Map daily spending for bar chart
  const barData = (stats?.daily_spending || []).map((item: any) => ({
    date: formatDate(item.date),
    amount: item.amount,
  }))

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      {/* Header */}
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Active Analysis
          </span>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900">Spending Overview</h1>
          <p className="mt-1 text-sm text-slate-600">
            Statement ID: <span className="font-mono text-xs text-slate-500">{statementId}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/upload")}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:border-slate-400 hover:bg-slate-50 transition"
          >
            Upload another
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="mb-8 grid gap-5 sm:grid-cols-3">
        {/* Total Debit */}
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-500">Total Spent</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 text-[#EF4444] border border-red-100/60">
              <ArrowUpRight className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatINR(stats?.total_debit || 0)}
            </h2>
            <p className="mt-1 text-xs text-slate-500 font-medium">Outflow across statement</p>
          </div>
        </div>

        {/* Total Credit */}
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-500">Total Received</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-[#10B981] border border-emerald-100/60">
              <ArrowDownRight className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              {formatINR(stats?.total_credit || 0)}
            </h2>
            <p className="mt-1 text-xs text-slate-500 font-medium">Inflow across statement</p>
          </div>
        </div>

        {/* Net Savings */}
        <div className={[
          "rounded-lg border p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300 bg-white",
          (stats?.net_savings || 0) >= 0 ? "border-emerald-200 bg-emerald-50/10" : "border-red-200 bg-red-50/10"
        ].join(" ")}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-500">Net Savings</span>
            <div className={[
              "flex h-10 w-10 items-center justify-center rounded-lg border",
              (stats?.net_savings || 0) >= 0 ? "bg-emerald-50 text-[#10B981] border-emerald-100" : "bg-red-50 text-[#EF4444] border-red-100"
            ].join(" ")}>
              <Wallet className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <h2 className={`text-2xl font-bold tracking-tight ${(stats?.net_savings || 0) >= 0 ? "text-emerald-700" : "text-red-700"}`}>
              {formatINR(stats?.net_savings || 0)}
            </h2>
            <p className="mt-1 text-xs text-slate-500 font-medium">
              Savings Rate: <span className="font-semibold text-slate-700">{stats?.savings_rate || 0}%</span>
            </p>
          </div>
        </div>
      </div>

      {/* Charts section */}
      <div className="mb-8 grid gap-6 lg:grid-cols-12">
        {/* Spending by Category */}
        <div className="lg:col-span-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Spending by Category</h2>
            <p className="text-xs text-slate-500 mb-6">Distribution of debits across main categories.</p>
          </div>
          {donutData.length > 0 ? (
            <div className="relative flex flex-col items-center justify-center">
              <SpendingDonut data={donutData} />
              {/* Donut chart legend */}
              <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-2 w-full text-xs">
                {donutData.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700 truncate">{item.name}</span>
                    <span className="font-medium text-slate-900 ml-auto">{formatINR(item.amount)}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-slate-500 text-sm">
              No debit transactions found to display.
            </div>
          )}
        </div>

        {/* Daily Spending Trend */}
        <div className="lg:col-span-7 rounded-lg border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-1">Daily Spending Trend</h2>
            <p className="text-xs text-slate-500 mb-6">Daily cash outflows tracked over the statement period.</p>
          </div>
          {barData.length > 0 ? (
            <DailyBarChart data={barData} />
          ) : (
            <div className="flex h-64 items-center justify-center text-slate-500 text-sm">
              No spending data available.
            </div>
          )}
        </div>
      </div>

      {/* Transaction Table */}
      <div className="mt-8">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Transactions</h2>
          <p className="text-xs text-slate-500">List of transactions parsed from the statement.</p>
        </div>
        <TransactionTable transactions={transactions} onTransactionUpdated={fetchData} />
      </div>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-10 animate-pulse">
      {/* Header Skeleton */}
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center">
        <div>
          <div className="h-6 w-32 rounded bg-slate-200" />
          <div className="mt-3 h-8 w-64 rounded bg-slate-200" />
          <div className="mt-2 h-4 w-96 rounded bg-slate-200" />
        </div>
        <div className="h-10 w-36 rounded bg-slate-200" />
      </div>

      {/* Summary Cards Skeleton */}
      <div className="mb-8 grid gap-5 sm:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex justify-between">
              <div className="h-4 w-24 rounded bg-slate-200" />
              <div className="h-10 w-10 rounded bg-slate-200" />
            </div>
            <div className="mt-4">
              <div className="h-8 w-32 rounded bg-slate-200" />
              <div className="mt-2 h-3.5 w-40 rounded bg-slate-200" />
            </div>
          </div>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="mb-8 grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm h-[400px]">
          <div className="h-5 w-40 rounded bg-slate-200 mb-6" />
          <div className="mx-auto h-48 w-48 rounded-full border-8 border-slate-100 flex items-center justify-center" />
        </div>
        <div className="lg:col-span-7 rounded-lg border border-slate-200 bg-white p-6 shadow-sm h-[400px]">
          <div className="h-5 w-40 rounded bg-slate-200 mb-6" />
          <div className="w-full h-64 rounded bg-slate-100" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <DashboardContent />
    </Suspense>
  )
}
