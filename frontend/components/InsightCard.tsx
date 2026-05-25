import { AlertTriangle, CheckCircle2, Info, Lightbulb } from "lucide-react";
import type { Insight } from "@/types";

const severityIcon = {
  success: CheckCircle2,
  warning: AlertTriangle,
  error: AlertTriangle,
  info: Info,
};

const severityColor = {
  success: "text-emerald-500",
  warning: "text-amber-500",
  error: "text-red-500",
  info: "text-blue-500",
};

export function InsightCard({ insight }: { insight: Insight }) {
  const Icon = severityIcon[insight.severity] ?? Lightbulb;
  const iconColor = severityColor[insight.severity] ?? "text-slate-500";

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className={`p-2 rounded-lg bg-slate-50 ${iconColor} shrink-0`}>
          <Icon className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900">{insight.title}</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">{insight.body}</p>
        </div>
      </div>
    </article>
  );
}

