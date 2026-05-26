import Link from "next/link";
import { Upload } from "lucide-react";

export function EmptyState() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center justify-center text-center p-8 border border-slate-200 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-[#10B981] mb-5 border border-emerald-100">
        <Upload className="h-5 w-5" aria-hidden />
      </div>
      <h2 className="text-xl font-semibold text-slate-900 tracking-tight">No statement loaded</h2>
      <p className="mt-2 text-sm leading-relaxed text-slate-650">
        Upload your bank statement (CSV or PDF) or load the demo dataset to view your spending dashboard, trends, and plain-language insights.
      </p>
      <Link
        href="/upload"
        className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-[#10B981] px-5 text-sm font-medium text-white hover:bg-emerald-600 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] shadow-sm hover:shadow"
      >
        Upload your first statement
      </Link>
    </div>
  );
}

