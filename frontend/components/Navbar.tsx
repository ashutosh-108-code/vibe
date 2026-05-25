"use client"

import Link from "next/link"
import { usePathname, useSearchParams } from "next/navigation"
import { BarChart3, Lightbulb, Upload } from "lucide-react"
import { Suspense } from "react"

const navItems = [
  { href: "/dashboard", label: "Dashboard", Icon: BarChart3 },
  { href: "/upload", label: "Upload", Icon: Upload },
  { href: "/insights", label: "Insights", Icon: Lightbulb },
]

function NavLinks() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const statementId = searchParams.get("statement_id")

  return (
    <nav className="flex items-center gap-2">
      {navItems.map(({ href, label, Icon }) => {
        // Append statement_id if it exists to maintain statement session context
        const targetHref = statementId && href !== "/upload"
          ? `${href}?statement_id=${statementId}`
          : href

        const isActive = pathname === href

        return (
          <Link
            key={href}
            href={targetHref}
            className={[
              "flex h-10 items-center gap-2 rounded-lg px-3.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-white/15 text-white"
                : "text-slate-300 hover:bg-white/5 hover:text-white"
            ].join(" ")}
          >
            <Icon className="h-4 w-4" aria-hidden />
            <span>{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

export function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-[#1E293B] text-white shadow-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/dashboard" className="flex items-center gap-2 text-lg font-bold tracking-tight hover:opacity-90 transition-opacity">
          <span className="bg-emerald-500 text-slate-900 rounded-md p-1.5 text-xs font-black leading-none">FT</span>
          <span>Finance Tracker</span>
        </Link>
        
        <Suspense fallback={<div className="h-10 w-64 bg-white/5 rounded-lg animate-pulse" />}>
          <NavLinks />
        </Suspense>
      </div>
    </header>
  )
}
