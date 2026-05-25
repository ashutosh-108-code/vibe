import type { Category } from "@/types";
import { CATEGORY_CONFIG } from "@/lib/categories";

export function CategoryBadge({ category }: { category: Category }) {
  const config = CATEGORY_CONFIG[category];
  if (!config) {
    return (
      <span className="inline-flex items-center rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
        {category}
      </span>
    );
  }

  const { bgClass, textClass, Icon } = config;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${bgClass} ${textClass}`}>
      <Icon className="h-3 w-3" aria-hidden />
      {category}
    </span>
  );
}

