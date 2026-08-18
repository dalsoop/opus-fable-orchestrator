#!/usr/bin/env python3
"""Print the Cursor Task slug for a read-only consult child.

Default is Cursor CLI Fable (`claude-fable-5-thinking-high`).
If agent-model-registry is on PATH, its id is mapped onto the allowlist
(exact, then prefix, then contains). Missing registry is not an error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

CURSOR_FABLE = "claude-fable-5-thinking-high"
DEFAULT_ALLOW = [
    "claude-fable-5-thinking-high",
    "claude-opus-5-thinking-high",
    "claude-sonnet-5-thinking-high",
    "cursor-grok-4.5-high-fast",
    "cursor-grok-4.6-medium",
    "gemini-3.7-flash-high",
    "gpt-5.6-sol-medium",
    "gpt-5.6-terra-medium",
    "composer-2.5-fast",
    "inherit",
]


def registry_get(name: str) -> str | None:
    bin_ = shutil.which("agent-model-registry")
    if not bin_:
        return None
    p = subprocess.run([bin_, "get", name], capture_output=True, text=True)
    if p.returncode != 0:
        return None
    line = (p.stdout or "").strip()
    return line.splitlines()[-1].strip() if line else None


def map_to_allowlist(rid: str, allow: list[str]) -> str | None:
    if rid in allow:
        return rid
    for a in allow:
        if a.startswith(rid) or rid in a:
            return a
    key = rid.lower()
    for needle, pred in (
        ("fable", lambda a: "fable" in a),
        ("grok", lambda a: "grok" in a),
        ("gpt", lambda a: a.startswith("gpt-")),
        ("gemini", lambda a: "gemini" in a),
        ("opus", lambda a: "opus" in a and "5-thinking" in a),
    ):
        if needle in key:
            for a in allow:
                if pred(a):
                    return a
    return None


def resolve(name: str, allow: list[str]) -> tuple[str | None, str]:
    rid = registry_get(name)
    raw = rid or name
    slug = map_to_allowlist(raw, allow)
    if name.lower() in {"fable", "default"} and not slug:
        slug = CURSOR_FABLE
    if not slug:
        slug = map_to_allowlist("fable", allow) or CURSOR_FABLE
    if "fable" in name.lower() and not rid:
        slug = CURSOR_FABLE
    return rid, slug


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="fable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    allow = [x.strip() for x in os.environ.get("CONSULT_ALLOWLIST", "").split(",") if x.strip()] or DEFAULT_ALLOW
    rid, slug = resolve(args.name, allow)
    if args.json:
        print(json.dumps({"registry": rid, "slug": slug, "name": args.name}))
    else:
        print(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
