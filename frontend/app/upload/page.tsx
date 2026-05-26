"use client"

import { ChangeEvent, DragEvent, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { FileText, Loader2, Sparkles, Upload, Wand2 } from "lucide-react"
import { getApiErrorMessage, loadDemo, uploadStatement } from "@/lib/api"

const progressMessages = [
  "Scanning statement...",
  "Categorizing transactions...",
  "Building your dashboard...",
]

type UploadResponseShape = {
  statementId?: string
  statement_id?: string
}

export default function UploadPage() {
  const router = useRouter()
  const inputRef = useRef<HTMLInputElement | null>(null)
  const timerRef = useRef<number | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [statusIndex, setStatusIndex] = useState(0)
  const [selectedFileName, setSelectedFileName] = useState("")
  const [error, setError] = useState("")
  const [toasts, setToasts] = useState<{ id: string; message: string; type: "success" | "error" }[]>([])

  const addToast = (message: string, type: "success" | "error" = "error") => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4500)
  }

  useEffect(() => {
    if (!isUploading) {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current)
        timerRef.current = null
      }
      setStatusIndex(0)
      return
    }

    timerRef.current = window.setInterval(() => {
      setStatusIndex((current) => (current < progressMessages.length - 1 ? current + 1 : current))
    }, 1100)

    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [isUploading])

  const openPicker = () => {
    inputRef.current?.click()
  }

  const handleFileSelection = async (file: File | null) => {
    if (!file) {
      return
    }

    setError("")
    setSelectedFileName(file.name)
    setIsUploading(true)

    try {
      const response = (await uploadStatement(file)) as UploadResponseShape
      const statementId = response.statementId ?? response.statement_id

      if (!statementId) {
        throw new Error("Upload completed, but no statement ID was returned.")
      }

      addToast("Statement uploaded successfully!", "success")
      setTimeout(() => {
        router.push(`/dashboard?statement_id=${statementId}`)
      }, 1200)
    } catch (err) {
      const message = getApiErrorMessage(err)
      addToast(message, "error")
      setError(message)
      setIsUploading(false)
    }
  }

  const handleInputChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    await handleFileSelection(file)
    event.target.value = ""
  }

  const handleDrop = async (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files?.[0] ?? null
    await handleFileSelection(file)
  }

  const handleDemoClick = async () => {
    setError("")
    setSelectedFileName("Demo data")
    setIsUploading(true)

    try {
      const response = (await loadDemo()) as UploadResponseShape
      const statementId = response.statementId ?? response.statement_id

      if (!statementId) {
        throw new Error("Demo loaded, but no statement ID was returned.")
      }

      addToast("Demo statements loaded successfully!", "success")
      setTimeout(() => {
        router.push(`/dashboard?statement_id=${statementId}`)
      }, 1200)
    } catch (err) {
      const message = getApiErrorMessage(err)
      addToast(message, "error")
      setError(message)
      setIsUploading(false)
    }
  }

  return (
    <section className="mx-auto max-w-5xl px-6 py-10">
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 bg-[#1E293B] px-8 py-8 text-white">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-400">
            Statement Upload
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-100">Drop in a CSV or PDF and we will do the heavy lifting.</h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-300">
            Upload a bank statement, let the ML pipeline classify each transaction, and jump
            straight into your dashboard.
          </p>
        </div>

        <div className="grid gap-6 px-8 py-8 lg:grid-cols-[1.35fr_0.85fr]">
          <div
            onDragOver={(event) => {
              event.preventDefault()
              if (!isUploading) {
                setIsDragging(true)
              }
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={[
              "rounded-lg border border-dashed p-8 transition-all duration-300",
              isDragging ? "border-[#10B981] bg-emerald-50/50" : "border-slate-300 bg-slate-50/50 hover:border-slate-450 hover:bg-slate-50",
              isUploading ? "pointer-events-none opacity-80" : "",
            ].join(" ")}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".csv,.pdf"
              className="hidden"
              onChange={handleInputChange}
            />

            <div className="flex min-h-[320px] flex-col items-center justify-center text-center">
              {isUploading ? (
                <>
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50 border border-emerald-100">
                    <Loader2 className="h-8 w-8 animate-spin text-[#10B981]" aria-hidden />
                  </div>
                  <p className="mt-6 text-lg font-semibold text-slate-900 tracking-tight">
                    {progressMessages[statusIndex]}
                  </p>
                  <p className="mt-2 text-sm text-slate-500 font-medium">
                    {selectedFileName ? `Working on ${selectedFileName}` : "Preparing upload"}
                  </p>
                </>
              ) : (
                <>
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-55 bg-emerald-50 text-[#10B981] border border-emerald-100 transition-transform duration-300 hover:scale-105">
                    <Upload className="h-6 w-6" aria-hidden />
                  </div>
                  <h2 className="mt-6 text-2xl font-semibold text-slate-900 tracking-tight">
                    Drag and drop your statement
                  </h2>
                  <p className="mt-3 max-w-md text-sm leading-relaxed text-slate-500">
                    We support bank statement CSVs and PDFs. Once uploaded, we parse, categorize,
                    and prepare your dashboard automatically.
                  </p>
                  <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                    <button
                      type="button"
                      onClick={openPicker}
                      className="inline-flex h-10 items-center justify-center rounded-lg bg-[#10B981] px-5 text-sm font-medium text-white transition-all duration-200 hover:bg-emerald-600 hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] shadow-sm hover:shadow"
                    >
                      Choose file
                    </button>
                    <button
                      type="button"
                      onClick={handleDemoClick}
                      className="inline-flex h-10 items-center justify-center rounded-lg border border-slate-300 bg-white px-5 text-sm font-medium text-slate-700 transition-all duration-200 hover:border-slate-400 hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] shadow-sm hover:shadow-sm"
                    >
                      Load Demo
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          <aside className="grid gap-4 rounded-lg bg-slate-50 p-5 border border-slate-200/60">
            <div className="rounded-lg border border-slate-200/80 bg-white p-4 shadow-sm hover:shadow hover:-translate-y-0.5 transition-all duration-300">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-[#F59E0B] border border-amber-100 shrink-0">
                  <FileText className="h-5 w-5" aria-hidden />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Accepted formats</h3>
                  <p className="text-xs text-slate-500 mt-0.5">CSV and PDF statements up to 10MB.</p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200/80 bg-white p-4 shadow-sm hover:shadow hover:-translate-y-0.5 transition-all duration-300">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-[#06B6D4] border border-cyan-100 shrink-0">
                  <Sparkles className="h-5 w-5" aria-hidden />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">What happens next</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Parsing, categorization, anomaly detection, and dashboard summary generation.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200/80 bg-white p-4 shadow-sm hover:shadow hover:-translate-y-0.5 transition-all duration-300">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-[#8B5CF6] border border-violet-100 shrink-0">
                  <Wand2 className="h-5 w-5" aria-hidden />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Demo mode</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Jump in with seeded mock transactions if you want to explore the flow first.
                  </p>
                </div>
              </div>
            </div>

            {error ? (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-xs font-medium text-red-800 animate-pulse">
                {error}
              </div>
            ) : null}
          </aside>
        </div>
      </div>

      {/* Toast Overlay */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-md w-full sm:w-auto">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={[
              "flex items-center gap-3 rounded-lg border px-4 py-3 text-sm font-medium shadow-lg transition-all duration-300 transform translate-y-0 animate-in fade-in slide-in-from-bottom-5",
              toast.type === "error"
                ? "border-red-200 bg-red-50 text-red-800"
                : "border-emerald-200 bg-emerald-50 text-emerald-800",
            ].join(" ")}
          >
            <span>{toast.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((t) => t.id !== toast.id))}
              className="ml-auto text-xs opacity-60 hover:opacity-100 font-bold px-1.5"
              aria-label="Close notification"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}
