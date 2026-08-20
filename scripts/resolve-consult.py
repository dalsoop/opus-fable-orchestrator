#!/usr/bin/env python3
"""Print a host-native model slug for a read-only consult child.

Family id: agent-model-registry `get fable` (fallback `claude-fable-5`).
Host: CONSULT_HOST, else this session (CURSOR_AGENT / CLAUDECODE / Codex / GROK_AGENT).
Cursor Task slugs are used only when the host is Cursor. Never treat a
random `agent` binary on PATH as Cursor.

Default JSON includes `fallback_name` / `fallback_slug` (grok) and `spawn`.
`--record` appends one line to ~/.orchestrator-consultant-gate/receipts.jsonl.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FAMILY = "claude-fable-5"
FALLBACK_NAME = "grok"
HOSTS = ("cursor", "claude", "codex", "grok")
RECEIPT = Path.home() / ".orchestrator-consultant-gate" / "receipts.jsonl"


def registry_get(name: str) -> str | None:
    bin_ = shutil.which("agent-model-registry")
    if not bin_:
        return None
    p = subprocess.run([bin_, "get", name], capture_output=True, text=True)
    if p.returncode != 0:
        return None
    line = (p.stdout or "").strip()
    return line.splitlines()[-1].strip() if line else None


def detect_host() -> str:
    raw = os.environ.get("CONSULT_HOST", "").strip().lower()
    if raw in HOSTS:
        return raw
    if os.environ.get("CURSOR_AGENT") == "1" or os.environ.get("CURSOR_INVOKED_AS"):
        return "cursor"
    if os.environ.get("CLAUDECODE") in ("1", "true") or os.environ.get("CLAUDE_CODE"):
        return "claude"
    if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_INTERNAL_ORIGINATOR_OVERRIDE"):
        return "codex"
    if os.environ.get("GROK_AGENT") == "1" or os.environ.get("GROK_SESSION_ID"):
        return "grok"
    return "unknown"


def parse_slugs(text: str) -> list[str]:
    slugs: list[str] = []
    for line in text.splitlines():
        token = line.strip().split()[0] if line.strip() else ""
        if token and token[0].isalpha() and "-" in token:
            slugs.append(token)
    return slugs


def list_cursor_models() -> list[str]:
    bin_ = shutil.which("cursor")
    if not bin_:
        return []
    p = subprocess.run([bin_, "--list-models"], capture_output=True, text=True, timeout=30)
    if p.returncode != 0 or not (p.stdout or "").strip():
        return []
    return parse_slugs(p.stdout)


def allowlist(host: str) -> list[str]:
    env = [x.strip() for x in os.environ.get("CONSULT_ALLOWLIST", "").split(",") if x.strip()]
    if env:
        return env
    if host == "cursor":
        return list_cursor_models()
    return []


def map_to_allowlist(rid: str, allow: list[str]) -> str | None:
    if not allow:
        return rid
    if rid in allow:
        return rid
    for a in allow:
        if a.startswith(rid) or rid in a:
            return a
    key = rid.lower()
    for needle in ("fable", "grok", "gpt", "gemini", "opus"):
        if needle not in key:
            continue
        for a in allow:
            al = a.lower()
            if needle == "opus" and "opus" in al and "fable" not in al:
                return a
            if needle != "opus" and needle in al:
                return a
    return None


def prefer_fable(host: str, allow: list[str], family: str) -> str:
    if host == "cursor" and allow:
        for a in allow:
            if a == f"{family}-thinking-high" or (family in a and "thinking-high" in a and "xhigh" not in a):
                return a
        for a in allow:
            if "fable" in a:
                return a
    return family


def resolve(name: str, host: str, allow: list[str]) -> tuple[str | None, str]:
    rid = registry_get(name)
    want_fable = "fable" in name.lower()
    raw = rid or (FAMILY if want_fable else name)
    mapped = map_to_allowlist(raw, allow)
    if mapped:
        return rid, mapped
    if want_fable:
        return rid, prefer_fable(host, allow, rid or FAMILY)
    return rid, raw


def spawn_hint(host: str, slug: str) -> dict[str, str]:
    return {
        "read_only": "no files, no tools; critic, not a second executor",
        "cursor": f'Task({{ description: "Consult", subagent_type: "generalPurpose", model: "{slug}", prompt: <briefing> }})',
        "claude": f'Agent({{ model: "{slug}", prompt: <briefing> }})',
        "codex": f"-m {slug}",
        "grok": (
            f'spawn_subagent({{ description: "Consult", subagent_type: "general-purpose", '
            f'model: "{slug}", prompt: <briefing> }}). '
            f'If the host cannot spawn that slug, blocked → fallback_slug. '
            f'Fable: `claude -p --model {slug} --max-turns 1` when Claude CLI can run the critic.'
        ),
        "host": host,
    }


def payload(name: str, host: str, allow: list[str]) -> dict:
    rid, slug = resolve(name, host, allow)
    out: dict = {
        "host": host,
        "registry": rid,
        "slug": slug,
        "name": name,
        "role": "critic",
        "allow_count": len(allow),
        "read_only": True,
        "spawn": spawn_hint(host, slug),
    }
    if name.lower() != FALLBACK_NAME:
        frid, fslug = resolve(FALLBACK_NAME, host, allow)
        out["fallback_name"] = FALLBACK_NAME
        out["fallback_registry"] = frid
        out["fallback_slug"] = fslug
    return out


def record(data: dict) -> Path:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(data, ensure_ascii=False)
    with RECEIPT.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return RECEIPT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="fable")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--record", action="store_true", help="append a receipt line")
    ap.add_argument("--ok", action="store_true")
    ap.add_argument("--read-only", action="store_true")
    ap.add_argument("--fallback-used", action="store_true")
    args = ap.parse_args()
    host = detect_host()
    allow = allowlist(host)
    data = payload(args.name, host, allow)
    if args.record:
        rec = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": data["host"],
            "name": data["name"],
            "slug": data["fallback_slug"] if args.fallback_used else data["slug"],
            "registry": data.get("fallback_registry") if args.fallback_used else data.get("registry"),
            "fallback_used": args.fallback_used,
            "spawn_ok": args.ok,
            "read_only": args.read_only,
        }
        path = record(rec)
        if args.json:
            rec["receipt"] = str(path)
            print(json.dumps(rec))
        else:
            print(path)
        return 0
    if args.json:
        print(json.dumps(data))
    else:
        print(data["slug"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
