import { AlertTriangle, CheckCircle2, Info, Lightbulb } from "lucide-react";
import type { Insight } from "@/types";

const severityIcon = {
  success: CheckCircle2,
  warning: AlertTriangle,
  error: AlertTriangle,
  info: Info,
};

const severityColor = {
  success: "text-emerald-600",
  warning: "text-amber-600",
  error: "text-red-600",
  info: "text-blue-600",
};

const severityBorderColor = {
  success: "border-l-emerald-500",
  warning: "border-l-amber-500",
  error: "border-l-red-500",
  info: "border-l-blue-500",
};

export function InsightCard({ insight }: { insight: Insight }) {
  const Icon = severityIcon[insight.severity] ?? Lightbulb;
  const iconColor = severityColor[insight.severity] ?? "text-slate-500";
  const borderLeftColor = severityBorderColor[insight.severity] ?? "border-l-slate-400";

  return (
    <article className={`rounded-lg border border-slate-200 border-l-4 bg-white p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 ${borderLeftColor}`}>
      <div className="flex items-start gap-4">
        <div className={`p-2 rounded-lg bg-slate-50 ${iconColor} shrink-0 border border-slate-100`}>
          <Icon className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900 tracking-tight">{insight.title}</h2>
          <p className="mt-1 text-sm leading-relaxed text-slate-600">{insight.body}</p>
        </div>
      </div>
    </article>
  );
}

