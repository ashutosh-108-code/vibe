import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        "ft-navy": "#1E293B",
        "ft-bg": "#F8FAFC",
        "ft-success": "#10B981",
        "ft-warning": "#F59E0B",
        "ft-error": "#EF4444",
        "ft-neutral": "#64748B",
      },
    },
  },
  plugins: [],
};
export default config;
