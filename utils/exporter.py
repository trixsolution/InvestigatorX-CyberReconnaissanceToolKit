"""
utils/exporter.py
Export scan results to JSON and TXT formats.
"""

import os
import json
from datetime import datetime
from typing import Any

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")


def ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def export_json(data: dict | list, module_name: str) -> str:
    """Export data as JSON and return the file path."""
    ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module_name}_{ts}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    payload = {
        "tool": "Investigator X – Cyber Recon Toolkit",
        "module": module_name,
        "generated_at": datetime.now().isoformat(),
        "results": data,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    return filepath


def export_txt(lines: list[str], module_name: str) -> str:
    """Export data as plain text and return the file path."""
    ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module_name}_{ts}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    header = [
        "=" * 60,
        "  Investigator X – Cyber Recon Toolkit",
        f"  Module  : {module_name}",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(header + lines))

    return filepath


def list_reports() -> list[dict]:
    """Return metadata for all saved reports."""
    ensure_reports_dir()
    reports = []
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        fpath = os.path.join(REPORTS_DIR, fname)
        stat = os.stat(fpath)
        reports.append(
            {
                "name": fname,
                "path": fpath,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )
    return reports
