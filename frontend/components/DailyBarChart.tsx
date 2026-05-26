"use client";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatINR, formatINRCompact } from "@/lib/formatters";

type DailySpend = {
  date: string;
  amount: number;
};

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 border border-slate-750 border-slate-800 text-white px-3.5 py-2.5 rounded-lg shadow-lg text-xs">
        <p className="font-medium text-slate-400 mb-1">{label}</p>
        <p className="font-bold text-emerald-400 text-sm">
          {formatINR(payload[0].value)}
        </p>
      </div>
    );
  }
  return null;
}

export function DailyBarChart({ data = [] }: { data?: DailySpend[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fill: "#64748B", fontSize: 11 }} />
          <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => formatINRCompact(v)} tick={{ fill: "#64748B", fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(100, 116, 139, 0.05)", radius: 8 }} />
          <Bar dataKey="amount" fill="#10B981" radius={[6, 6, 0, 0]} maxBarSize={45} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
