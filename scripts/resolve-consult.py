#!/usr/bin/env python3
"""Print a host-native model slug for a read-only consult child.

Family id: agent-model-registry `get fable` (fallback `claude-fable-5`).
Host: CONSULT_HOST, else this session (CURSOR_AGENT / CLAUDECODE / Codex / GROK_AGENT).
Cursor Task slugs are used only when the host is Cursor. Never treat a
random `agent` binary on PATH as Cursor.

`--list` prints selectable critics. `--report` is usage history from receipts (not critic quality).
Default JSON includes `fallbacks` (opus 4.6 first) plus legacy `fallback_slug`.
`--record` appends one line to ~/.orchestrator-consultant-gate/receipts.jsonl.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

FAMILY = "claude-fable-5"
LIST_NAMES = ("fable", "opus", "grok", "gpt", "gemini")
FALLBACK_NAMES = ("opus", "grok")
OPUS_GEN = "opus-4-6"
WINDOW_1M = "[1m]"
HOSTS = ("cursor", "claude", "codex", "grok")
HOOK_NAME = "block-hand-claude-p.py"
HOOK_TIMEOUT_S = 3
STYLE_NAME = "consult-gate-brief"
STATE = Path(os.environ.get("ORCHESTRATOR_CONSULT_HOME", str(Path.home() / ".orchestrator-consultant-gate")))
RECEIPT = STATE / "receipts.jsonl"
LIST_STAMP = STATE / "last-list.json"
LIST_MAX_AGE_SEC = 3600


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


def with_1m(base: str) -> str:
    if not base or WINDOW_1M in base:
        return base
    return f"{base}{WINDOW_1M}"


def generation_ok(rid: str | None, gen: str) -> bool:
    if not rid:
        return False
    return gen in rid.lower().replace(".", "-")


def map_same_family(rid: str, allow: list[str]) -> str | None:
    """Keep the registry family. Do not remap opus-4-6 onto opus-5."""
    if not allow:
        return rid
    if rid in allow:
        return rid
    bare = rid.replace(WINDOW_1M, "")
    for a in allow:
        if a == rid or a == bare or a.startswith(bare + "["):
            return a
    return rid


def resolve(name: str, host: str, allow: list[str]) -> tuple[str | None, str]:
    rid = registry_get(name)
    n = name.lower()
    want_fable = "fable" in n
    raw = rid or (FAMILY if want_fable else name)
    if n == "opus":
        return rid, map_same_family(with_1m(raw), allow)
    mapped = map_to_allowlist(raw, allow)
    if mapped:
        return rid, mapped
    if want_fable:
        return rid, prefer_fable(host, allow, rid or FAMILY)
    return rid, raw


def spawn_hint(host: str, slug: str) -> dict[str, str]:
    cursor = (
        f'Task({{ description: "Consult", subagent_type: "generalPurpose", '
        f'model: "{slug}", prompt: <briefing> }}). '
        f'If Task is blocked, pick opus from `--list` (4.6). Do not use grok first.'
    )
    if slug.startswith("claude-") or "fable" in slug.lower():
        grok = (
            f'First: `claude -p --model {slug} --max-turns 3 --disable-slash-commands`. '
            f'Do not start with spawn_subagent. '
            f'spawn_subagent only if Claude CLI is missing and the slug is a Grok model.'
        )
        first = "claude -p"
    elif slug.startswith("grok-"):
        grok = f'spawn_subagent({{ model: "{slug}" }}) on Grok. Do not pass this slug to claude -p.'
        first = "spawn_subagent"
    else:
        grok = "Unresolved. Pick a resolved name from `--list`."
        first = "skip"
    return {
        "read_only": "no files, no tools; critic, not a second executor",
        "first": first,
        "cursor": cursor,
        "claude": f'Agent({{ model: "{slug}", prompt: <briefing> }})',
        "codex": f"-m {slug}",
        "grok": grok,
        "host": host,
    }


def catalog_item(name: str, host: str, allow: list[str]) -> dict:
    rid, slug = resolve(name, host, allow)
    spawn = spawn_hint(host, slug)
    resolved = bool(rid) or (name == "fable")
    item: dict = {
        "name": name,
        "registry": rid,
        "slug": slug,
        "resolved": resolved,
        "selectable": resolved,
        "gate_default": name == "fable",
        "gate_blocked": name == "opus",
        "spawn_first": spawn["first"],
        "spawn": spawn,
    }
    if name == "opus":
        item["generation"] = OPUS_GEN
        item["generation_ok"] = generation_ok(rid, OPUS_GEN)
        item["selectable"] = bool(item["generation_ok"])
    return item


def list_critics(host: str, allow: list[str]) -> dict:
    critics = [catalog_item(n, host, allow) for n in LIST_NAMES]
    return {"host": host, "role": "critic", "critics": critics}


def claude_spawn_line(slug: str) -> str:
    return f"claude -p --model {slug} --max-turns 3 --disable-slash-commands"


def line_hash(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:16]


def patch_stamp(**fields: object) -> dict | None:
    stamp = load_list_stamp()
    if not stamp:
        return None
    stamp.update(fields)
    STATE.mkdir(parents=True, exist_ok=True)
    LIST_STAMP.write_text(json.dumps(stamp), encoding="utf-8")
    return stamp


def session_id() -> str:
    host = os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION")
    if host:
        return host
    return os.environ.get("CONSULT_SESSION") or "default"


def prepare_claude_spawn(name: str, data: dict) -> tuple[str, int]:
    if not require_listed(name):
        return "", 2
    first = (data.get("spawn") or {}).get("first")
    if first != "claude -p":
        print(
            f"spawn_first={first!r}; Grok spawn is only for fable/opus. pick a listed name",
            file=sys.stderr,
        )
        return "", 2
    if (load_list_stamp() or {}).get("spawn_used"):
        print("run --list first; spawn-line already recorded", file=sys.stderr)
        return "", 2
    line = claude_spawn_line(data["slug"])
    if not patch_stamp(
        spawn_line=line,
        spawn_hash=line_hash(line),
        spawn_name=name.lower(),
    ):
        print("run --list first this turn", file=sys.stderr)
        return "", 2
    return line, 0


def exec_claude(line: str, briefing: Path) -> int:
    parts = line.split()
    bin_ = shutil.which(parts[0]) if parts else None
    if not bin_:
        print("claude not on PATH", file=sys.stderr)
        return 2
    env = {**os.environ, "CONSULT_EXEC": "1"}
    with briefing.open("r", encoding="utf-8") as stdin:
        p = subprocess.run([bin_, *parts[1:]], stdin=stdin, env=env)
    return p.returncode


def hook_script() -> Path:
    installed = Path.home() / ".claude" / "skills" / "orchestrator-consultant-gate" / "scripts" / HOOK_NAME
    if installed.is_file():
        return installed.resolve()
    return (Path(__file__).resolve().parent / HOOK_NAME).resolve()


def install_hook(settings: Path, script: Path) -> dict:
    settings.parent.mkdir(parents=True, exist_ok=True)
    if settings.is_file():
        data = json.loads(settings.read_text(encoding="utf-8"))
    else:
        data = {}
    hooks = data.setdefault("hooks", {})
    pre = list(hooks.get("PreToolUse") or [])
    kept = []
    for grp in pre:
        hs = [h for h in (grp.get("hooks") or []) if HOOK_NAME not in (h.get("command") or "")]
        if hs:
            nxt = dict(grp)
            nxt["hooks"] = hs
            kept.append(nxt)
        elif (grp.get("matcher") or "") != "Bash":
            kept.append(grp)
    kept.append(
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {script}",
                    "timeout": HOOK_TIMEOUT_S,
                }
            ],
        }
    )
    hooks["PreToolUse"] = kept
    bak = None
    if settings.is_file():
        bak = settings.with_name(settings.name + ".bak-consult-hook")
        bak.write_text(settings.read_text(encoding="utf-8"), encoding="utf-8")
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"settings": str(settings), "script": str(script), "backup": str(bak) if bak else None}


def claude_settings_paths() -> tuple[Path, Path]:
    settings = Path(
        os.environ.get("ORCHESTRATOR_CONSULT_HOOK_SETTINGS")
        or str(Path.home() / ".claude" / "settings.json")
    )
    styles = Path(
        os.environ.get("ORCHESTRATOR_CONSULT_OUTPUT_STYLES")
        or str(Path.home() / ".claude" / "output-styles")
    )
    return settings, styles


def style_src() -> Path:
    return Path(__file__).resolve().parent.parent / "output-styles" / f"{STYLE_NAME}.md"


def install_claude(settings: Path, styles_dir: Path, force_style: bool) -> dict:
    src = style_src()
    if not src.is_file():
        print(f"missing {src}", file=sys.stderr)
        return {"error": "missing style", "settings": str(settings)}
    styles_dir.mkdir(parents=True, exist_ok=True)
    dest = styles_dir / f"{STYLE_NAME}.md"
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    settings.parent.mkdir(parents=True, exist_ok=True)
    bak = None
    if settings.is_file():
        data = json.loads(settings.read_text(encoding="utf-8"))
        bak = settings.with_name(settings.name + ".bak-consult-claude")
        bak.write_text(settings.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        data = {}
    host = detect_host()
    rid, slug = resolve("opus", host, allowlist(host))
    data["model"] = slug
    prev = data.get("outputStyle")
    style_set = False
    if force_style or not prev:
        data["outputStyle"] = STYLE_NAME
        style_set = True
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    body = dest.read_text(encoding="utf-8")
    return {
        "settings": str(settings),
        "model": slug,
        "generation": OPUS_GEN,
        "generation_ok": generation_ok(rid, OPUS_GEN),
        "outputStyle": data.get("outputStyle"),
        "outputStyle_set": style_set,
        "outputStyle_kept": None if style_set else prev,
        "style_file": str(dest),
        "keep_coding_instructions": "keep-coding-instructions: true" in body,
        "claude_md_written": False,
        "env_opus": os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL"),
        "backup": str(bak) if bak else None,
    }


def uninstall_claude(settings: Path, styles_dir: Path) -> dict:
    dest = styles_dir / f"{STYLE_NAME}.md"
    removed_file = False
    if dest.is_file():
        dest.unlink()
        removed_file = True
    if not settings.is_file():
        return {
            "settings": str(settings),
            "removed_style_file": removed_file,
            "outputStyle_removed": False,
            "model_unchanged": True,
        }
    data = json.loads(settings.read_text(encoding="utf-8"))
    style_removed = False
    if data.get("outputStyle") == STYLE_NAME:
        data.pop("outputStyle", None)
        style_removed = True
        settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "settings": str(settings),
        "removed_style_file": removed_file,
        "outputStyle_removed": style_removed,
        "model_unchanged": True,
        "model": data.get("model"),
    }


def uninstall_hook(settings: Path) -> dict:
    if not settings.is_file():
        return {"settings": str(settings), "removed": 0}
    data = json.loads(settings.read_text(encoding="utf-8"))
    pre = list((data.get("hooks") or {}).get("PreToolUse") or [])
    kept = []
    removed = 0
    for grp in pre:
        hs = [h for h in (grp.get("hooks") or []) if HOOK_NAME not in (h.get("command") or "")]
        removed += len((grp.get("hooks") or [])) - len(hs)
        if hs:
            nxt = dict(grp)
            nxt["hooks"] = hs
            kept.append(nxt)
        elif (grp.get("matcher") or "") != "Bash":
            kept.append(grp)
    if "hooks" not in data:
        data["hooks"] = {}
    data["hooks"]["PreToolUse"] = kept
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"settings": str(settings), "removed": removed}


def save_list_stamp(data: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    stamp = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": data.get("host"),
        "session": session_id(),
        "names": [c["name"] for c in data.get("critics") or [] if c.get("selectable")],
    }
    LIST_STAMP.write_text(json.dumps(stamp), encoding="utf-8")


def load_list_stamp() -> dict | None:
    if not LIST_STAMP.is_file():
        return None
    try:
        stamp = json.loads(LIST_STAMP.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    raw = stamp.get("ts") or ""
    try:
        ts = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    if age > LIST_MAX_AGE_SEC:
        return None
    if stamp.get("session") != session_id():
        return None
    return stamp


def require_listed(name: str) -> bool:
    stamp = load_list_stamp()
    if not stamp:
        print("run --list first this turn", file=sys.stderr)
        return False
    names = stamp.get("names") or []
    if name.lower() not in names:
        print(f"{name} not selectable in last --list", file=sys.stderr)
        return False
    return True


def report_receipts() -> dict:
    rows: list[dict] = []
    if RECEIPT.is_file():
        for line in RECEIPT.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    by: dict[str, dict] = {}
    for r in rows:
        key = f"{r.get('name') or '?'}|{r.get('slug') or '?'}|{r.get('host') or '?'}"
        slot = by.setdefault(
            key,
            {
                "name": r.get("name"),
                "slug": r.get("slug"),
                "host": r.get("host"),
                "n": 0,
                "spawn_ok": 0,
                "fallback_used": 0,
            },
        )
        slot["n"] += 1
        if r.get("spawn_ok"):
            slot["spawn_ok"] += 1
        if r.get("fallback_used"):
            slot["fallback_used"] += 1
    return {
        "receipt": str(RECEIPT),
        "n": len(rows),
        "note": "usage history; not critic quality",
        "by": list(by.values()),
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
    fallbacks = []
    for n in FALLBACK_NAMES:
        if n == name.lower():
            continue
        frid, fslug = resolve(n, host, allow)
        item: dict = {"name": n, "registry": frid, "slug": fslug}
        if n == "opus":
            item["generation"] = OPUS_GEN
            item["generation_ok"] = generation_ok(frid, OPUS_GEN)
        fallbacks.append(item)
    out["fallbacks"] = fallbacks
    if fallbacks:
        first = fallbacks[0]
        out["fallback_name"] = first["name"]
        out["fallback_registry"] = first["registry"]
        out["fallback_slug"] = first["slug"]
        if first["name"] == "opus":
            out["fallback_generation"] = first.get("generation")
            out["fallback_generation_ok"] = first.get("generation_ok")
    if name.lower() == "opus":
        out["generation"] = OPUS_GEN
        out["generation_ok"] = generation_ok(rid, OPUS_GEN)
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
    ap.add_argument("--list", action="store_true", help="selectable critics")
    ap.add_argument("--report", action="store_true", help="usage history from receipts")
    ap.add_argument("--record", action="store_true", help="append a receipt line")
    ap.add_argument("--ok", action="store_true")
    ap.add_argument("--read-only", action="store_true")
    ap.add_argument("--fallback-used", action="store_true")
    ap.add_argument("--print-spawn", action="store_true", help="print Grok claude -p line; requires --list")
    ap.add_argument("--exec-spawn", action="store_true", help="run stamped claude -p and record; Grok only")
    ap.add_argument("--briefing", default="", help="briefing file for --exec-spawn")
    ap.add_argument("--dry-run", action="store_true", help="with --exec-spawn, print the line and do not exec")
    ap.add_argument("--spawn-line", default="", help="exact --print-spawn stdout; required with --record")
    ap.add_argument("--install-hook", action="store_true", help="wire Claude Code PreToolUse(Bash); Grok has none")
    ap.add_argument("--uninstall-hook", action="store_true", help="remove the PreToolUse(Bash) consult hook")
    ap.add_argument("--install-claude", action="store_true", help="pin opus 4.6 + write outputStyle; not CLAUDE.md")
    ap.add_argument("--uninstall-claude", action="store_true", help="drop this skill's outputStyle and style file")
    ap.add_argument("--force-output-style", action="store_true", help="overwrite an existing outputStyle")
    args = ap.parse_args()
    if args.install_claude or args.uninstall_claude:
        settings, styles = claude_settings_paths()
        out = (
            install_claude(settings, styles, args.force_output_style)
            if args.install_claude
            else uninstall_claude(settings, styles)
        )
        if out.get("error"):
            return 2
        if args.json:
            print(json.dumps(out))
        else:
            print(out["settings"])
        return 0
    if args.install_hook or args.uninstall_hook:
        settings = Path(
            os.environ.get("ORCHESTRATOR_CONSULT_HOOK_SETTINGS")
            or str(Path.home() / ".claude" / "settings.json")
        )
        out = (
            install_hook(settings, hook_script())
            if args.install_hook
            else uninstall_hook(settings)
        )
        if args.json:
            print(json.dumps(out))
        else:
            print(out["settings"])
        return 0
    host = detect_host()
    allow = allowlist(host)
    if args.list:
        data = list_critics(host, allow)
        save_list_stamp(data)
        if args.json:
            print(json.dumps(data))
        else:
            print(f"host={data['host']}")
            for c in data["critics"]:
                mark = "default" if c["gate_default"] else ("blocked" if c["gate_blocked"] else "override")
                if not c["selectable"]:
                    mark = "skip"
                print(f"{c['name']:8} {c.get('registry') or '-':22} {c['slug']:28} {mark} spawn={c['spawn_first']}")
        return 0
    if args.report:
        data = report_receipts()
        if args.json:
            print(json.dumps(data))
        else:
            print(f"n={data['n']} {data['note']}")
            for row in data["by"]:
                print(
                    f"{row['name']} {row['slug']} host={row['host']} "
                    f"n={row['n']} ok={row['spawn_ok']} fallback={row['fallback_used']}"
                )
        return 0
    data = payload(args.name, host, allow)
    stamp = load_list_stamp()
    data["list_ok"] = bool(stamp) and args.name.lower() in (stamp.get("names") or [])
    if args.print_spawn:
        line, rc = prepare_claude_spawn(args.name, data)
        if rc:
            return rc
        print(line)
        return 0
    if args.exec_spawn:
        line, rc = prepare_claude_spawn(args.name, data)
        if rc:
            return rc
        if args.dry_run:
            print(line)
            return 0
        briefing = Path(args.briefing) if args.briefing else None
        if briefing is None or not briefing.is_file():
            print("--exec-spawn needs --briefing FILE or --dry-run", file=sys.stderr)
            return 2
        code = exec_claude(line, briefing)
        rec = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": data["host"],
            "name": data["name"],
            "slug": data["slug"],
            "registry": data.get("registry"),
            "fallback_used": False,
            "spawn_ok": code == 0,
            "read_only": True,
            "listed": True,
            "executed": True,
            "spawn_hash": line_hash(line),
        }
        path = record(rec)
        patch_stamp(spawn_used=True)
        if args.json:
            rec["receipt"] = str(path)
            print(json.dumps(rec))
        else:
            print(path)
        return 0 if code == 0 else 1
    if args.record:
        if not require_listed(args.name):
            return 2
        stamp = load_list_stamp() or {}
        want = stamp.get("spawn_hash")
        got_line = args.spawn_line.strip()
        if stamp.get("spawn_used"):
            print("spawn-line already recorded this stamp", file=sys.stderr)
            return 2
        if not want or not got_line or line_hash(got_line) != want:
            print("pass --spawn-line from this turn's --print-spawn", file=sys.stderr)
            return 2
        rec = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": data["host"],
            "name": data["name"],
            "slug": data["fallback_slug"] if args.fallback_used else data["slug"],
            "registry": data.get("fallback_registry") if args.fallback_used else data.get("registry"),
            "fallback_used": args.fallback_used,
            "spawn_ok": args.ok,
            "read_only": args.read_only,
            "listed": True,
            "spawn_hash": want,
        }
        path = record(rec)
        patch_stamp(spawn_used=True)
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
