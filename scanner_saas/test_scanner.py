"""Test scanner module"""
import sys
sys.path.insert(0, "C:/Projects/mimo/scanner_saas")

from backend.core.scanner import run_scan

results = run_scan("Bishkek", "dental", 3)

print(f"Found {len(results)} businesses")
for r in results:
    name = r['name'].encode('ascii', 'replace').decode('ascii')
    print(f"  - {name}: Score {r['score']}, Loss ${r['monthly_loss_estimate']}")
