// frontend/lib/categories.ts
import {
  UtensilsCrossed, Car, ShoppingCart, Home,
  CreditCard, ShoppingBag, TrendingUp, MoreHorizontal,
} from "lucide-react"
import type { Category } from "@/types"

export const CATEGORY_CONFIG: Record<Category, {
  color: string
  bgClass: string
  textClass: string
  Icon: React.ElementType
}> = {
  Food:        { color: "#F59E0B", bgClass: "bg-amber-100",   textClass: "text-amber-800",  Icon: UtensilsCrossed },
  Transport:   { color: "#3B82F6", bgClass: "bg-blue-100",    textClass: "text-blue-800",   Icon: Car },
  Groceries:   { color: "#10B981", bgClass: "bg-emerald-100", textClass: "text-emerald-800",Icon: ShoppingCart },
  Rent:        { color: "#8B5CF6", bgClass: "bg-violet-100",  textClass: "text-violet-800", Icon: Home },
  EMI:         { color: "#EF4444", bgClass: "bg-red-100",     textClass: "text-red-800",    Icon: CreditCard },
  Shopping:    { color: "#EC4899", bgClass: "bg-pink-100",    textClass: "text-pink-800",   Icon: ShoppingBag },
  Investments: { color: "#06B6D4", bgClass: "bg-cyan-100",    textClass: "text-cyan-800",   Icon: TrendingUp },
  Other:       { color: "#64748B", bgClass: "bg-slate-100",   textClass: "text-slate-800",  Icon: MoreHorizontal },
}
