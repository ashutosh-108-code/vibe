"""Quick local E2E API test for Finance Tracker."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8000"


def req(method: str, path: str, data: bytes | None = None, headers: dict | None = None):
    request = urllib.request.Request(
        BASE + path,
        data=data,
        headers=headers or {},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=60) as resp:
        return resp.status, json.loads(resp.read())


def main() -> None:
    print("=== Finance Tracker Local Test ===\n")

    _, health = req("GET", "/health")
    print(f"[1] Health: {health}")
    assert health.get("status") == "ok"

    _, demo = req("POST", "/api/demo")
    sid = demo["statement_id"]
    print(f"[2] Demo: {demo['message']}")
    print(f"    statement_id: {sid}")

    _, stats = req("GET", f"/api/stats?statement_id={sid}&period=monthly")
    cat_count = sum(1 for v in stats["by_category"].values() if v["amount"] > 0)
    print(
        f"[3] Stats: debit={stats['total_debit']:,.0f}, "
        f"credit={stats['total_credit']:,.0f}, "
        f"categories={cat_count}, "
        f"daily_points={len(stats['daily_spending'])}"
    )
    assert stats["total_debit"] > 0
    assert len(stats["daily_spending"]) > 0

    _, ins_en = req("GET", f"/api/insights?statement_id={sid}&language=en")
    print(f"[4] Insights (EN): {len(ins_en['insights'])} items")
    for item in ins_en["insights"]:
        print(f"    - [{item['severity']}] {item['title']}")
    assert len(ins_en["insights"]) >= 3

    _, ins_hi = req("GET", f"/api/insights?statement_id={sid}&language=hi")
    print(f"[5] Insights (HI): {len(ins_hi['insights'])} items")
    assert len(ins_hi["insights"]) >= 3

    _, txs = req("GET", f"/api/transactions?statement_id={sid}&limit=100")
    print(f"[6] Transactions: {txs['total']} total")
    target = next((t for t in txs["transactions"] if t["category"] != "Food"), txs["transactions"][0])
    body = json.dumps({"category": "Food"}).encode()
    _, patch = req(
        "PATCH",
        f"/api/transactions/{target['id']}/category",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    print(f"[7] Re-categorize: {target['category']} -> {patch['new_category']}")

    print("\n=== ALL TESTS PASSED ===")
    print(f"\nOpen in browser: http://localhost:3000/upload")
    print(f"Then Load Demo -> dashboard?statement_id={sid}")


if __name__ == "__main__":
    main()
