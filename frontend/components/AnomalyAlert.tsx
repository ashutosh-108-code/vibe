import { AlertTriangle } from "lucide-react";

export function AnomalyAlert({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      <AlertTriangle className="mt-0.5 h-4 w-4" aria-hidden />
      <p>{message}</p>
    </div>
  );
}
