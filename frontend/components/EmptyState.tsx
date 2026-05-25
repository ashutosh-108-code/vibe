import Link from "next/link";
import { Upload } from "lucide-react";

export function EmptyState() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center justify-center text-center p-8 border border-slate-200 bg-white rounded-lg shadow-sm">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-[#10B981] mb-4">
        <Upload className="h-6 w-6" aria-hidden />
      </div>
      <h2 className="text-xl font-semibold text-slate-900">No bank statement loaded</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        Upload your bank statement (CSV or PDF) or load the demo dataset to view your spending dashboard, trends, and plain-language insights.
      </p>
      <Link
        href="/upload"
        className="mt-6 inline-flex h-10 items-center justify-center rounded-lg bg-[#10B981] px-5 text-sm font-medium text-white hover:bg-emerald-600 transition shadow-sm"
      >
        Upload your first statement
      </Link>
    </div>
  );
}

