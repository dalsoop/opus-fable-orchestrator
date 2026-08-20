#!/usr/bin/env python3
"""Claude Code PreToolUse(Bash): deny hand-typed critic `claude -p`.

Allow resolve-consult.py (the wrapper). Grok has no PreToolUse.
"""

from __future__ import annotations

import json
import re
import sys

PRINT_FLAG = re.compile(
    r"(?:^|[\s;|&`'\"])(?:\S+/)?claude(?:\s+\S+)*\s+(?:-p|--print)(?:\s|=|$)",
    re.I,
)
WRAPPER = "resolve-consult.py"


def command_body(cmd: str) -> str:
    lines = []
    for line in cmd.splitlines():
        lines.append(line.split("#", 1)[0])
    return " ".join(lines)


def decide(payload: dict) -> str | None:
    tool = payload.get("tool_name") or ""
    if tool and tool != "Bash":
        return None
    inp = payload.get("tool_input")
    if not isinstance(inp, dict):
        inp = {}
    cmd = inp.get("command") or payload.get("command") or ""
    if not isinstance(cmd, str) or WRAPPER in command_body(cmd):
        return None
    if PRINT_FLAG.search(cmd):
        return (
            "Hand-typed claude -p is blocked. "
            "Use python3 scripts/resolve-consult.py --exec-spawn --briefing FILE"
        )
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0
    reason = decide(payload)
    if not reason:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
