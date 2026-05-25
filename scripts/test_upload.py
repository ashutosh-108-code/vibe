"""Test file upload against local API."""
import json
import sys
from pathlib import Path

try:
    import urllib.request
except ImportError:
    sys.exit(1)

CSV = """Date,Narration,Withdrawal Amt.,Deposit Amt.,Closing Balance
01/05/2026,UPI-SWIGGY-ORDER-123456,450.00,,49550.00
02/05/2026,NEFT-SALARY CREDIT,,145000.00,194550.00
03/05/2026,POS-FLIPKART-PAYMENT,2499.00,,192051.00
"""

BASE = "http://127.0.0.1:8000"


def upload_with_boundary(boundary: str, include_boundary_in_header: bool) -> None:
    body_parts = [
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
        f"{CSV}\r\n"
        f"--{boundary}--\r\n",
    ]
    data = "".join(body_parts).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/api/upload", data=data, method="POST")
    if include_boundary_in_header:
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    else:
        req.add_header("Content-Type", "multipart/form-data")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read())
            print("OK", resp.status, payload.get("statement_id"), payload.get("total_transactions"))
    except Exception as exc:
        print("FAIL", include_boundary_in_header, exc)


def upload_multipart_lib() -> None:
  try:
    import requests
  except ImportError:
    print("requests not installed, skip")
    return
  files = {"file": ("test.csv", CSV.encode("utf-8"), "text/csv")}
  r = requests.post(f"{BASE}/api/upload", files=files, timeout=60)
  print("requests", r.status_code, r.json().get("statement_id") if r.ok else r.text[:200])


if __name__ == "__main__":
    upload_multipart_lib()
    upload_with_boundary("testboundary123", True)
    upload_with_boundary("testboundary123", False)
