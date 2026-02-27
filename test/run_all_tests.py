#!/usr/bin/env python3
"""
ServiceNow MCP Server — Test Runner
====================================
Discovers and runs every test script under test/, captures output,
parses pass/fail markers, and writes results to a timestamped CSV.

Usage:
    python3 test/run_all_tests.py
"""

import asyncio
import csv
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = PROJECT_ROOT / "test"
RESULTS_DIR = PROJECT_ROOT / "test_results"
PER_TEST_TIMEOUT = 180  # seconds

# Module mapping: derive a human-readable module name from the file path
MODULE_MAP = {
    "incident": "Incident Management",
    "change_manage": "Change Management",
    "catelog": "Service Catalog",
    "agile_manage": "Agile / Project",
    "client_catalog_full": "Service Catalog",
    "client_incident_full": "Incident Management",
    "client_update_set_full": "Update Set Management",
    "client_update_set": "Update Set Management",
    "client_cmdb": "CMDB Management",
    "client_problem": "Problem Management",
    "client_sla": "SLA Management",
    "client_table_crud": "Table CRUD",
    "client_kb": "Knowledge Base",
    "client_user": "User Management",
    "client_request": "Request Management",
    "client_analytic": "Analytics",
    "client_workf_man": "Workflow Management",
    "client_script_man": "Script Include Management",
    "client_ui_policy": "UI Policy Management",
}


def resolve_module(test_path: Path) -> str:
    """Return a friendly module name for the test file."""
    rel = test_path.relative_to(TEST_DIR)
    parts = rel.parts
    # Check subdirectory first
    if len(parts) > 1:
        subdir = parts[0]
        if subdir in MODULE_MAP:
            return MODULE_MAP[subdir]
    # Then check stem
    stem = test_path.stem
    if stem in MODULE_MAP:
        return MODULE_MAP[stem]
    return stem


def discover_tests() -> list[Path]:
    """Find all test scripts, excluding this runner itself."""
    tests = []
    for p in sorted(TEST_DIR.rglob("*.py")):
        if p.name == "run_all_tests.py":
            continue
        if p.name.startswith("__"):
            continue
        tests.append(p)
    return tests


def parse_output(output: str) -> dict:
    """Parse test output for pass/fail/skip markers and extract details."""
    passes = re.findall(r"✅.*", output)
    failures = re.findall(r"❌.*", output)
    skips = re.findall(r"⚠️.*", output)

    # Build a short detail string: first failure reason or first pass
    detail_lines = []
    for line in failures[:3]:
        clean = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
        detail_lines.append(clean[:120])
    if not detail_lines:
        for line in passes[:2]:
            clean = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
            detail_lines.append(clean[:120])

    return {
        "passed": len(passes),
        "failed": len(failures),
        "skipped": len(skips),
        "details": " | ".join(detail_lines) if detail_lines else "",
    }


def run_single_test(test_path: Path) -> dict:
    """Run a single test file and return result dict."""
    module = resolve_module(test_path)
    rel_path = test_path.relative_to(PROJECT_ROOT)

    print(f"  Running {rel_path} ...", end=" ", flush=True)
    start = time.monotonic()

    try:
        proc = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=PER_TEST_TIMEOUT,
            cwd=str(PROJECT_ROOT),
        )
        elapsed = round(time.monotonic() - start, 1)
        output = proc.stdout + proc.stderr
        parsed = parse_output(output)

        # Determine overall status
        if proc.returncode != 0 and parsed["passed"] == 0:
            status = "CRASH"
            if not parsed["details"]:
                # Grab last meaningful line from stderr
                err_lines = [l.strip() for l in proc.stderr.strip().splitlines() if l.strip()]
                parsed["details"] = (err_lines[-1][:120] if err_lines else f"exit code {proc.returncode}")
        elif parsed["failed"] > 0:
            status = "PARTIAL"
        elif parsed["passed"] > 0:
            status = "PASS"
        else:
            status = "UNKNOWN"

    except subprocess.TimeoutExpired:
        elapsed = PER_TEST_TIMEOUT
        status = "TIMEOUT"
        parsed = {"passed": 0, "failed": 0, "skipped": 0, "details": f"Timed out after {PER_TEST_TIMEOUT}s"}

    # Status emoji for console
    emoji = {"PASS": "✅", "PARTIAL": "⚠️ ", "CRASH": "❌", "TIMEOUT": "⏰", "UNKNOWN": "❓"}.get(status, "?")
    print(f"{emoji} {status}  ({parsed['passed']}P/{parsed['failed']}F/{parsed['skipped']}S) [{elapsed}s]")

    return {
        "file": str(rel_path),
        "module": module,
        "status": status,
        "passed": parsed["passed"],
        "failed": parsed["failed"],
        "skipped": parsed["skipped"],
        "duration_s": elapsed,
        "details": parsed["details"],
    }


def print_summary_table(results: list[dict], total_duration: float):
    """Print a formatted table to the console."""
    # Column widths
    w_file = max(len(r["file"]) for r in results)
    w_mod = max(len(r["module"]) for r in results)
    w_file = max(w_file, 9)
    w_mod = max(w_mod, 6)

    header = f"{'Test File':<{w_file}}  {'Module':<{w_mod}}  {'Status':<8}  {'Pass':>4}  {'Fail':>4}  {'Skip':>4}  {'Time':>6}"
    sep = "-" * len(header)

    print(f"\n{'=' * len(header)}")
    print("TEST RESULTS SUMMARY")
    print(f"{'=' * len(header)}")
    print(header)
    print(sep)

    for r in results:
        emoji = {"PASS": "✅", "PARTIAL": "⚠️ ", "CRASH": "❌", "TIMEOUT": "⏰"}.get(r["status"], "  ")
        print(
            f"{r['file']:<{w_file}}  {r['module']:<{w_mod}}  {emoji}{r['status']:<6}  "
            f"{r['passed']:>4}  {r['failed']:>4}  {r['skipped']:>4}  {r['duration_s']:>5.1f}s"
        )

    print(sep)

    total_p = sum(r["passed"] for r in results)
    total_f = sum(r["failed"] for r in results)
    total_s = sum(r["skipped"] for r in results)
    files_pass = sum(1 for r in results if r["status"] == "PASS")
    files_fail = sum(1 for r in results if r["status"] in ("PARTIAL", "CRASH", "TIMEOUT"))

    print(f"\nFiles: {len(results)} total, {files_pass} passed, {files_fail} with issues")
    print(f"Checks: {total_p} passed, {total_f} failed, {total_s} skipped")
    print(f"Total time: {total_duration:.1f}s")


def write_csv(results: list[dict], run_time: datetime, total_duration: float) -> Path:
    """Write results to a timestamped CSV file and return the path."""
    RESULTS_DIR.mkdir(exist_ok=True)

    total_p = sum(r["passed"] for r in results)
    total_f = sum(r["failed"] for r in results)
    ts = run_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"test_results_{ts}_P{total_p}_F{total_f}.csv"
    csv_path = RESULTS_DIR / filename

    fieldnames = [
        "file", "module", "status", "passed", "failed",
        "skipped", "duration_s", "run_date", "details",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        run_date_str = run_time.strftime("%Y-%m-%d %H:%M:%S")
        for r in results:
            row = {**r, "run_date": run_date_str}
            writer.writerow(row)

        # Summary row at the bottom
        writer.writerow({
            "file": "TOTAL",
            "module": f"{len(results)} files",
            "status": "PASS" if total_f == 0 else "PARTIAL",
            "passed": total_p,
            "failed": total_f,
            "skipped": sum(r["skipped"] for r in results),
            "duration_s": round(total_duration, 1),
            "run_date": run_date_str,
            "details": f"{sum(1 for r in results if r['status']=='PASS')}/{len(results)} files clean",
        })

    return csv_path


def main():
    run_time = datetime.now()
    print(f"ServiceNow MCP Server — Test Runner")
    print(f"Run started: {run_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = discover_tests()
    print(f"Discovered {len(tests)} test file(s).\n")

    start = time.monotonic()
    results = []
    for test_path in tests:
        result = run_single_test(test_path)
        results.append(result)

    total_duration = round(time.monotonic() - start, 1)

    print_summary_table(results, total_duration)

    csv_path = write_csv(results, run_time, total_duration)
    print(f"\nResults saved to: {csv_path}")


if __name__ == "__main__":
    main()
