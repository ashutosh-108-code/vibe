import { useMemo } from "react";
import type { Transaction } from "@/types";

export function useTransactions(transactions: Transaction[] = []) {
  return useMemo(() => ({ transactions, total: transactions.length }), [transactions]);
}
