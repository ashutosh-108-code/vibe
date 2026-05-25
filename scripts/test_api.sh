#!/usr/bin/env sh
set -eu

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

CSV_FILE="$TMP_DIR/hdfc_test.csv"
UPLOAD_JSON="$TMP_DIR/upload.json"
DEMO_JSON="$TMP_DIR/demo.json"
STATS_JSON="$TMP_DIR/stats.json"
INSIGHTS_JSON="$TMP_DIR/insights.json"
TRANSACTIONS_JSON="$TMP_DIR/transactions.json"
PATCH_JSON="$TMP_DIR/patch.json"

cat > "$CSV_FILE" <<'CSV'
Date,Narration,Withdrawal Amt.,Deposit Amt.,Closing Balance
01/05/2026,UPI-SWIGGY-ORDER-123456,450.00,,49550.00
02/05/2026,NEFT-SALARY CREDIT,,145000.00,194550.00
03/05/2026,POS-FLIPKART-PAYMENT,2499.00,,192051.00
CSV

status_of() {
  path="$1"
  shift
  curl -sS -o "$path" -w "%{http_code}" "$@"
}

assert_status() {
  name="$1"
  status="$2"
  expected="${3:-200}"
  if [ "$status" != "$expected" ]; then
    echo "FAIL $name expected $expected got $status"
    cat "$4"
    echo
    exit 1
  fi
  echo "PASS $name -> $status"
}

json_value() {
  file="$1"
  expr="$2"
  python -c "import json; data=json.load(open('$file', encoding='utf-8')); print($expr)"
}

health_status="$(status_of "$TMP_DIR/health.json" "$API_BASE/health")"
assert_status "GET /health" "$health_status" 200 "$TMP_DIR/health.json"
json_value "$TMP_DIR/health.json" "data['status']"

upload_status="$(status_of "$UPLOAD_JSON" -X POST "$API_BASE/api/upload" -F "file=@$CSV_FILE;type=text/csv")"
assert_status "POST /api/upload" "$upload_status" 200 "$UPLOAD_JSON"
upload_statement_id="$(json_value "$UPLOAD_JSON" "data['statement_id']")"
json_value "$UPLOAD_JSON" "list(data.keys())"

demo_status="$(status_of "$DEMO_JSON" -X POST "$API_BASE/api/demo")"
assert_status "POST /api/demo" "$demo_status" 200 "$DEMO_JSON"
demo_statement_id="$(json_value "$DEMO_JSON" "data['statement_id']")"
json_value "$DEMO_JSON" "list(data.keys())"

stats_status="$(status_of "$STATS_JSON" "$API_BASE/api/stats?statement_id=$demo_statement_id&period=monthly")"
assert_status "GET /api/stats" "$stats_status" 200 "$STATS_JSON"
json_value "$STATS_JSON" "list(data.keys())"

insights_status="$(status_of "$INSIGHTS_JSON" "$API_BASE/api/insights?statement_id=$demo_statement_id&language=en")"
assert_status "GET /api/insights" "$insights_status" 200 "$INSIGHTS_JSON"
json_value "$INSIGHTS_JSON" "list(data.keys())"

transactions_status="$(status_of "$TRANSACTIONS_JSON" "$API_BASE/api/transactions?statement_id=$demo_statement_id&page=1&limit=5")"
assert_status "GET /api/transactions" "$transactions_status" 200 "$TRANSACTIONS_JSON"
transaction_id="$(json_value "$TRANSACTIONS_JSON" "data['transactions'][0]['id']")"
json_value "$TRANSACTIONS_JSON" "list(data.keys())"

patch_status="$(status_of "$PATCH_JSON" -X PATCH "$API_BASE/api/transactions/$transaction_id/category" -H "Content-Type: application/json" -d '{"category":"Food"}')"
assert_status "PATCH /api/transactions/{id}/category" "$patch_status" 200 "$PATCH_JSON"
json_value "$PATCH_JSON" "list(data.keys())"

echo "All 7 endpoints returned 200 with expected response shapes."
echo "Upload statement_id: $upload_statement_id"
echo "Demo statement_id: $demo_statement_id"
