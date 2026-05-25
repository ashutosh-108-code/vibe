"use client"

import { useState, useMemo, useEffect } from "react"
import type { Category, Transaction } from "@/types"
import { CategoryBadge } from "./CategoryBadge"
import { formatINR, formatDate } from "@/lib/formatters"
import { recategorize } from "@/lib/api"
import { Search, Filter, AlertTriangle } from "lucide-react"

const CATEGORIES: Category[] = [
  "Food", "Transport", "Groceries", "Rent",
  "EMI", "Shopping", "Investments", "Other"
]

export function TransactionTable({
  transactions = [],
  onTransactionUpdated
}: {
  transactions?: Transaction[]
  onTransactionUpdated?: () => void
}) {
  const [localTransactions, setLocalTransactions] = useState<Transaction[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  // Sync props to local state
  useEffect(() => {
    setLocalTransactions(transactions)
  }, [transactions])

  const handleCategoryChange = async (transactionId: string, newCategory: Category) => {
    setUpdatingId(transactionId)
    try {
      await recategorize(transactionId, newCategory)
      
      // Update local state
      setLocalTransactions(prev =>
        prev.map(t =>
          t.id === transactionId
            ? { ...t, category: newCategory, manuallyUpdated: true }
            : t
        )
      )

      // Notify parent to refresh stats and charts
      if (onTransactionUpdated) {
        onTransactionUpdated()
      }
    } catch (err) {
      console.error("Failed to recategorize transaction:", err)
      alert("Failed to update category. Please try again.")
    } finally {
      setUpdatingId(null)
    }
  }

  // Filtered transactions
  const filteredTransactions = useMemo(() => {
    return localTransactions.filter(t => {
      const matchesSearch = t.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            t.rawDescription?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = categoryFilter === "all" || t.category === categoryFilter
      return matchesSearch && matchesCategory
    })
  }, [localTransactions, searchTerm, categoryFilter])

  return (
    <div className="space-y-4">
      {/* Search and Filter Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between bg-slate-50 p-4 rounded-lg border border-slate-200">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by merchant or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500 bg-white transition"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-sm border border-slate-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500 cursor-pointer"
          >
            <option value="all">All Categories</option>
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table container */}
      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm border-collapse">
          <thead className="bg-[#1E293B] text-white text-xs uppercase tracking-wider">
            <tr>
              <th className="px-5 py-3.5 font-medium">Date</th>
              <th className="px-5 py-3.5 font-medium">Merchant & Detail</th>
              <th className="px-5 py-3.5 font-medium">Category</th>
              <th className="px-5 py-3.5 font-medium text-right">Amount</th>
              <th className="px-5 py-3.5 font-medium">Type</th>
              <th className="px-5 py-3.5 font-medium text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredTransactions.length > 0 ? (
              filteredTransactions.map((transaction) => {
                const isAnomaly = transaction.isAnomaly || false
                return (
                  <tr
                    key={transaction.id}
                    className={[
                      "transition-colors hover:bg-slate-50/50",
                      isAnomaly ? "bg-red-50/80 border-l-4 border-[#EF4444]" : ""
                    ].join(" ")}
                  >
                    <td className="px-5 py-4 text-slate-600 whitespace-nowrap">
                      {formatDate(transaction.date)}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-semibold text-slate-900">{transaction.merchant}</div>
                      {transaction.rawDescription && (
                        <div className="text-xs text-slate-500 font-mono mt-0.5 truncate max-w-xs sm:max-w-md">
                          {transaction.rawDescription}
                        </div>
                      )}
                      {isAnomaly && transaction.anomalyReason && (
                        <div className="mt-1 flex items-center gap-1 text-xs font-medium text-[#EF4444]">
                          <AlertTriangle className="h-3 w-3 shrink-0" />
                          <span>{transaction.anomalyReason}</span>
                        </div>
                      )}
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap">
                      <CategoryBadge category={transaction.category} />
                    </td>
                    <td className="px-5 py-4 text-right font-semibold text-slate-900 whitespace-nowrap">
                      {formatINR(transaction.amount)}
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap">
                      <span className={[
                        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider",
                        transaction.type === "credit" ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-700"
                      ].join(" ")}>
                        {transaction.type}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-center whitespace-nowrap">
                      <div className="relative inline-block text-left">
                        <select
                          disabled={updatingId === transaction.id}
                          value={transaction.category}
                          onChange={(e) => handleCategoryChange(transaction.id, e.target.value as Category)}
                          className={[
                            "text-xs bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded px-2.5 py-1.5 font-medium transition focus:outline-none cursor-pointer",
                            updatingId === transaction.id ? "opacity-50 cursor-wait" : ""
                          ].join(" ")}
                        >
                          {CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>
                              {cat}
                            </option>
                          ))}
                        </select>
                      </div>
                    </td>
                  </tr>
                )
              })
            ) : (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-slate-500">
                  No transactions match your search or filter criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
