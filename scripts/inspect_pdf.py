"""Inspect bank statement PDF structure."""
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8")

path = Path(r"c:\Users\Ashutosh\Downloads\Statement_1779639430342_unlocked.pdf")
out = Path(__file__).resolve().parents[1] / "ml-engine" / "data" / "pdf_inspect.txt"

doc = fitz.open(str(path))
lines_out: list[str] = []
lines_out.append(f"pages={doc.page_count} size={path.stat().st_size}")

for i in range(doc.page_count):
    page = doc[i]
    text = page.get_text("text")
    lines_out.append(f"\n===== PAGE {i} ({len(text)} chars) =====\n")
    lines_out.append(text)

    try:
        finder = page.find_tables()
        tables = finder.tables if finder else []
        lines_out.append(f"\n--- tables on page {i}: {len(tables)} ---\n")
        for ti, table in enumerate(tables):
            df = table.to_pandas(dtype=str)
            lines_out.append(f"Table {ti} shape={df.shape}\n")
            lines_out.append(df.to_string())
            lines_out.append("\n")
    except Exception as exc:
        lines_out.append(f"table error: {exc}\n")

doc.close()
out.write_text("\n".join(lines_out), encoding="utf-8")
print(f"wrote {out}")
