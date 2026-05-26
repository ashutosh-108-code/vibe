"use client";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatINR } from "@/lib/formatters";

type SpendingSlice = {
  name: string;
  amount: number;
  color: string;
};

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="bg-slate-900 border border-slate-800 text-white px-3.5 py-2.5 rounded-lg shadow-lg text-xs">
        <div className="flex items-center gap-2 mb-1">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
          <span className="font-medium text-slate-300">{item.name}</span>
        </div>
        <p className="font-bold text-slate-100 text-sm">
          {formatINR(item.amount)}
        </p>
      </div>
    );
  }
  return null;
}

export function SpendingDonut({ data = [] }: { data?: SpendingSlice[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie 
            data={data} 
            dataKey="amount" 
            nameKey="name" 
            innerRadius={75} 
            outerRadius={100} 
            paddingAngle={2}
            stroke="#ffffff"
            strokeWidth={2}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
