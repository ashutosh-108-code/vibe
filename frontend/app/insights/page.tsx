"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { getInsights } from "@/lib/api"
import { EmptyState } from "@/components/EmptyState"
import { InsightCard } from "@/components/InsightCard"
import { AnomalyAlert } from "@/components/AnomalyAlert"
import type { Insight } from "@/types"
import { Sparkles, AlertCircle, RefreshCw, Languages } from "lucide-react"

function InsightsContent() {
  const searchParams = useSearchParams()
  const statementId = searchParams.get("statement_id")
  const router = useRouter()

  const [language, setLanguage] = useState<"en" | "hi">("en")
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState<Insight[]>([])
  const [error, setError] = useState("")

  const fetchInsightsData = async () => {
    if (!statementId) return
    setLoading(true)
    setError("")
    try {
      const response = await getInsights(statementId, language)
      setInsights(response.insights || [])
    } catch (err) {
      console.error(err)
      setError("Could not load spending insights. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (statementId) {
      fetchInsightsData()
    } else {
      setLoading(false)
    }
  }, [statementId, language])

  if (!statementId) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <EmptyState />
      </div>
    )
  }

  if (loading) {
    return <InsightsSkeleton />
  }

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center text-red-800 shadow-sm">
          <AlertCircle className="mx-auto h-12 w-12 text-[#EF4444] mb-3" />
          <h2 className="text-xl font-semibold">Error Loading Insights</h2>
          <p className="mt-2 text-sm">{error}</p>
          <div className="mt-4 flex justify-center gap-3">
            <button
              onClick={() => fetchInsightsData()}
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

  // Separate anomalies and standard insights
  const anomalyInsights = insights.filter(item => item.type === "anomaly")
  const standardInsights = insights.filter(item => item.type !== "anomaly")

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      {/* Header with Language Toggle */}
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-800">
            <Sparkles className="h-3 w-3" />
            AI-Generated Insights
          </span>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900">
            {language === "en" ? "Financial Insights" : "वित्तीय इनसाइट्स"}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {language === "en" 
              ? "Plain-language summary of your transaction behavior." 
              : "आपके लेन-देन व्यवहार का सरल भाषा में सारांश।"}
          </p>
        </div>
        <div>
          <button
            onClick={() => setLanguage(prev => prev === "en" ? "hi" : "en")}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-slate-400 hover:bg-slate-50 transition shadow-sm"
          >
            <Languages className="h-4 w-4 text-[#8B5CF6]" />
            <span>{language === "en" ? "हिंदी में देखें" : "Show in English"}</span>
          </button>
        </div>
      </div>

      {/* Anomalies Section */}
      {anomalyInsights.length > 0 && (
        <div className="mb-8 space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#EF4444]">
            {language === "en" ? "Critical Anomaly Warnings" : "महत्वपूर्ण विसंगति चेतावनियाँ"}
          </h2>
          <div className="space-y-3">
            {anomalyInsights.map((anomaly, idx) => (
              <AnomalyAlert key={idx} message={`${anomaly.title}: ${anomaly.body}`} />
            ))}
          </div>
        </div>
      )}

      {/* Standard Insights */}
      <div className="space-y-5">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {language === "en" ? "Observations & Recommendations" : "अवलोकन और सिफारिशें"}
        </h2>
        {standardInsights.length > 0 ? (
          <div className="grid gap-4">
            {standardInsights.map((insight, idx) => (
              <InsightCard key={idx} insight={insight} />
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-slate-200 bg-white p-8 text-center text-slate-500">
            {language === "en" 
              ? "No spending patterns detected for standard categories yet." 
              : "अभी तक मानक श्रेणियों के लिए कोई खर्च पैटर्न नहीं मिला है।"}
          </div>
        )}
      </div>
    </div>
  )
}

function InsightsSkeleton() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-10 animate-pulse">
      {/* Header Skeleton */}
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center">
        <div>
          <div className="h-6 w-36 rounded bg-slate-200" />
          <div className="mt-3 h-8 w-64 rounded bg-slate-200" />
          <div className="mt-2 h-4 w-80 rounded bg-slate-200" />
        </div>
        <div className="h-10 w-32 rounded bg-slate-200" />
      </div>

      {/* Anomalies Skeleton */}
      <div className="mb-8 space-y-3">
        <div className="h-4 w-48 rounded bg-slate-200" />
        <div className="h-16 w-full rounded bg-red-50/50 border border-red-100" />
      </div>

      {/* Standard Insights Skeletons */}
      <div className="space-y-4">
        <div className="h-4 w-56 rounded bg-slate-200 mb-2" />
        {[1, 2, 3].map(i => (
          <div key={i} className="h-24 w-full rounded-lg bg-slate-50 border border-slate-100" />
        ))}
      </div>
    </div>
  )
}

export default function InsightsPage() {
  return (
    <Suspense fallback={<InsightsSkeleton />}>
      <InsightsContent />
    </Suspense>
  )
}
