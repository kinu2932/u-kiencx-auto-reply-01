#!/usr/bin/env python3
"""The Funniest Auto-Reply an AI Ever Sent — make.fun entry.

Writes one out-of-office auto-reply (103 chars) to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output).

Self-check gate: refuses to write if the entry is not a single line
of 1-159 characters, so a bad edit can never ship an invalid entry.
"""
import os
from pathlib import Path

ENTRY = "Out of office: I'm at the beach. There is no beach. I have never seen a beach. I am still at the beach."

def main():
    if not 1 <= len(ENTRY) <= 159:
        raise SystemExit(f"entry length {len(ENTRY)} outside gate 1-159")
    if "\n" in ENTRY or "\r" in ENTRY:
        raise SystemExit("entry must be a single line")
    if not ENTRY.strip():
        raise SystemExit("entry must not be only whitespace")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "entry.txt").write_text(ENTRY, encoding="utf-8")

if __name__ == "__main__":
    main()
