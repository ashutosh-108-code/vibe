import { Upload } from "lucide-react";

export function UploadZone() {
  return (
    <div className="flex min-h-80 flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
      <Upload className="h-10 w-10 text-[#10B981]" aria-hidden />
      <h1 className="mt-4 text-xl font-semibold text-slate-900">Upload bank statement</h1>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
        CSV and PDF parsing will be wired in the upload workflow.
      </p>
    </div>
  );
}
