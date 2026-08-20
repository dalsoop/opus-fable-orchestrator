#!/usr/bin/env python3
"""Static eval for this skill checkout. Live Fable scenarios skip unless EVAL_LIVE=1."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = json.loads((ROOT / "eval" / "eval.json").read_text(encoding="utf-8"))


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        raise SystemExit("SKILL.md: missing YAML frontmatter")
    out: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for line in m.group(1).splitlines():
        if re.match(r"^[a-zA-Z0-9_]+:", line) and not line.startswith(" "):
            if key is not None:
                out[key] = "\n".join(buf).strip().strip("\"'")
            key, _, rest = line.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == ">|" or rest == ">":
                buf = []
            else:
                buf = [rest]
        elif key is not None:
            buf.append(line.strip())
    if key is not None:
        out[key] = "\n".join(buf).strip().strip("\"'")
    meta = re.search(r"^metadata:\n((?:  .*\n)+)", m.group(1) + "\n", re.M)
    if meta:
        vm = re.search(r"version:\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)", meta.group(1))
        if vm:
            out["metadata.version"] = vm.group(1)
    return out


def fail(sid: str, msg: str) -> dict:
    return {"id": sid, "ok": False, "detail": msg}


def ok(sid: str, detail: str = "") -> dict:
    return {"id": sid, "ok": True, "detail": detail}


def run() -> int:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    fm = frontmatter(skill_text)
    version = (ROOT / EVAL["version_file"]).read_text(encoding="utf-8").strip()
    desc = re.sub(r"\s+", " ", fm.get("description", ""))
    name = fm.get("name", "")
    live = os.environ.get("EVAL_LIVE") == "1"
    results: list[dict] = []

    for sc in EVAL["scenarios"]:
        sid, typ = sc["id"], sc["type"]
        if sc.get("harness") == "live" and not live:
            results.append({"id": sid, "ok": True, "detail": "skipped (set EVAL_LIVE=1)", "skipped": True})
            continue
        if typ == "version":
            mv = fm.get("metadata.version", "")
            if not re.fullmatch(r"\d+\.\d+\.\d+", version):
                results.append(fail(sid, f"VERSION not semver: {version!r}"))
            elif mv != version:
                results.append(fail(sid, f"frontmatter {mv!r} != VERSION {version!r}"))
            elif name != EVAL["skill"]:
                results.append(fail(sid, f"name {name!r} != {EVAL['skill']!r}"))
            else:
                results.append(ok(sid, version))
        elif typ == "trigger" and sc["expect"] == "description_has_required_not_forbidden":
            missing = [t for t in EVAL["triggers_required"] if t not in desc]
            extra = [t for t in EVAL["triggers_forbidden"] if t in desc]
            if missing or extra:
                results.append(fail(sid, f"missing={missing} forbidden_present={extra}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "briefing_has_sections":
            brief = (ROOT / "templates" / "fable-briefing.md").read_text(encoding="utf-8")
            miss = [s for s in EVAL["briefing_sections"] if s not in brief]
            oq = EVAL["open_question"]
            if miss or oq not in brief:
                results.append(fail(sid, f"missing_sections={miss} open={oq in brief}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "digest_has_accept_reject_defer":
            digest = (ROOT / "templates" / "digest.md").read_text(encoding="utf-8")
            need = ["accept", "reject", "defer"]
            miss = [n for n in need if n not in digest]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc["expect"] == "skill_mentions_timeout_fallback":
            miss = [n for n in EVAL["timeout_needles"] if n.lower() not in skill_text.lower()]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc["expect"] == "skill_keeps_session_parent":
            miss = [n for n in EVAL.get("parent_needles", []) if n not in skill_text]
            extra = [n for n in EVAL.get("parent_forbidden", []) if n in skill_text]
            if miss or extra:
                results.append(fail(sid, f"missing={miss} forbidden_present={extra}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "resolve_consult_script":
            import json as _json
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            if not script.is_file():
                results.append(fail(sid, "missing scripts/resolve-consult.py"))
            else:
                p = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True)
                if p.returncode != 0:
                    results.append(fail(sid, p.stderr or p.stdout or "script failed"))
                else:
                    try:
                        data = _json.loads(p.stdout)
                    except _json.JSONDecodeError:
                        results.append(fail(sid, f"not json: {p.stdout!r}"))
                    else:
                        slug = data.get("slug") or ""
                        host = data.get("host") or ""
                        want = EVAL.get("fable_model_slug", "claude-fable-5")
                        fbs = {x.get("name"): x for x in (data.get("fallbacks") or []) if isinstance(x, dict)}
                        opus = fbs.get("opus") or {}
                        opus_id = ((opus.get("registry") or opus.get("slug") or "") + "").lower().replace(".", "-")
                        if "host" not in data:
                            results.append(fail(sid, "json missing host"))
                        elif want and want not in slug and "fable" not in slug.lower():
                            results.append(fail(sid, f"slug {slug!r} missing {want!r}"))
                        elif "grok" not in fbs:
                            results.append(fail(sid, f"fallbacks missing grok: {data.get('fallbacks')!r}"))
                        elif "opus" not in fbs:
                            results.append(fail(sid, f"fallbacks missing opus: {data.get('fallbacks')!r}"))
                        elif "opus-4-6" not in opus_id and opus.get("generation_ok") is not True:
                            results.append(fail(sid, f"opus is not 4.6: {opus!r}"))
                        elif not data.get("spawn") or not data.get("read_only"):
                            results.append(fail(sid, "json missing spawn/read_only"))
                        else:
                            results.append(ok(sid, f"{host}:{slug}"))
        elif sc["expect"] == "folder_matches_skill_name":
            if ROOT.name != EVAL["skill"]:
                results.append(fail(sid, f"folder {ROOT.name!r} != name {EVAL['skill']!r}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "skill_contains_fable_slug":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"resolve not json: {p.stdout!r}"))
            else:
                slug = data.get("slug") or ""
                if "fable" not in slug.lower():
                    results.append(fail(sid, f"resolve slug not fable: {slug!r}"))
                else:
                    results.append(ok(sid, slug))
        elif sc["expect"] == "skill_allows_consult_override":
            miss = [n for n in EVAL.get("override_needles", []) if n not in skill_text]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc.get("harness") == "live":
            import shutil
            import subprocess

            needle = sc.get("prompt_contains", "Rebut me")
            brief = (ROOT / "templates" / "fable-briefing.md").read_text(encoding="utf-8")
            if needle not in brief:
                results.append(fail(sid, f"briefing missing {needle!r}"))
                continue
            script = ROOT / "scripts" / "resolve-consult.py"
            r = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True)
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"resolve not json: {r.stdout!r}"))
                continue
            host = data.get("host")
            slugs = [data.get("slug")]
            fb = data.get("fallback_slug")
            if fb and fb not in slugs:
                slugs.append(fb)
            prompt = (
                "You are a read-only consultant. "
                + needle
                + ". Reply with the exact token REBUT_OK in the first line."
            )
            timeout = sc.get("timeout_seconds", 120)
            grok_via_claude = host == "grok"
            if grok_via_claude:
                slugs = [s for s in slugs if s and ("fable" in s.lower() or s.lower().startswith("claude-"))]
                if not slugs:
                    results.append(fail(sid, "no claude/fable slug for grok live"))
                    continue
            if host == "cursor":
                bin_ = shutil.which("cursor")
                if not bin_:
                    results.append(fail(sid, "cursor CLI not on PATH"))
                    continue

                def _cmd(model: str) -> list[str]:
                    return [bin_, "-p", "--mode", "ask", "--model", model, prompt]
            elif host == "claude" or grok_via_claude:
                bin_ = shutil.which("claude")
                if not bin_:
                    results.append(fail(sid, "claude CLI not on PATH"))
                    continue

                def _cmd(model: str) -> list[str]:
                    cmd = [bin_, "-p", "--model", model]
                    if grok_via_claude:
                        cmd.extend(["--max-turns", "1"])
                    cmd.append(prompt)
                    return cmd
            else:
                results.append({"id": sid, "ok": True, "detail": f"skipped live on host={host}", "skipped": True})
                continue
            last = ""
            used: str | bool | None = None
            skipped_trust = False
            for model in slugs:
                if not model:
                    continue
                p = subprocess.run(
                    _cmd(model),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(ROOT),
                )
                out = (p.stdout or "") + (p.stderr or "")
                last = out
                if "Workspace Trust Required" in out:
                    skipped_trust = True
                    break
                blocked = (
                    p.returncode != 0
                    or "Review Data Policy" in out
                    or "data policy" in out.lower()
                    or "HTTP 402" in out
                    or " 402" in out
                )
                if "REBUT_OK" in out:
                    used = model
                    break
                if not blocked:
                    results.append(fail(sid, f"missing REBUT_OK {out[-800:]}"))
                    used = False
                    break
            if used is False:
                pass
            elif skipped_trust:
                results.append({"id": sid, "ok": True, "detail": "skipped (cursor workspace trust)", "skipped": True})
            elif used:
                results.append(ok(sid, f"{host}:{used}"))
            else:
                results.append(fail(sid, f"all slugs blocked {last[-800:]}"))
        elif sc["expect"] == "no_legacy_skill_name":
            blob = skill_text + "\n" + (ROOT / "README.md").read_text(encoding="utf-8")
            if "opus-fable-orchestrator" in blob:
                results.append(fail(sid, "legacy skill name still present"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "cases_happy_hit_description":
            cases_path = ROOT / "evals" / "cases.json"
            if not cases_path.is_file():
                results.append(fail(sid, "missing evals/cases.json"))
            else:
                cases = json.loads(cases_path.read_text(encoding="utf-8"))
                miss = []
                for c in cases.get("cases", []):
                    if not c.get("should_trigger"):
                        continue
                    prompt = c.get("prompt", "")
                    if not any(t in prompt for t in EVAL["triggers_required"]):
                        miss.append(c["id"])
                results.append(fail(sid, f"happy missing locale triggers {miss}") if miss else ok(sid))
        elif sc["expect"] == "readme_not_a_skill":
            readme = (ROOT / "README.md").read_text(encoding="utf-8")
            if "For agents" in readme or "에이전트 전용" in readme:
                results.append(fail(sid, "README must not duplicate SKILL.md"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "readme_locale_diagram":
            readme = (ROOT / "README.md").read_text(encoding="utf-8")
            en = "how-the-gate-works-en.png" in readme
            ko = "how-the-gate-works-ko.png" in readme
            loc = EVAL.get("locale")
            if loc == "en" and (not en or ko):
                results.append(fail(sid, f"en branch wants en.png only (en={en} ko={ko})"))
            elif loc == "ko" and (not ko or en):
                results.append(fail(sid, f"ko branch wants ko.png only (en={en} ko={ko})"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "resolve_reports_host":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                host = data.get("host")
                slug = data.get("slug") or ""
                if host not in ("cursor", "claude", "codex", "grok", "unknown"):
                    results.append(fail(sid, f"bad host {host!r}"))
                elif "fable" not in slug.lower():
                    results.append(fail(sid, f"slug not fable: {slug!r}"))
                else:
                    results.append(ok(sid, f"{host}:{slug}"))
        elif sc["expect"] == "skill_fable_is_critic":
            miss = [n for n in EVAL.get("critic_needles", []) if n not in skill_text]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc["expect"] == "skill_mentions_observability":
            miss = [n for n in EVAL.get("observability_needles", ["--record", "fallback_slug"]) if n not in skill_text]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc["expect"] == "skill_names_other_consults":
            miss = [n for n in ("--name grok", "--name gpt", "--name gemini", "--name opus") if n not in skill_text]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc["expect"] == "resolve_named_consult":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run(
                [sys.executable, str(script), "--name", "grok", "--json"],
                capture_output=True,
                text=True,
            )
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                slug = data.get("slug") or ""
                if p.returncode != 0 or data.get("name") != "grok" or not slug:
                    results.append(fail(sid, f"rc={p.returncode} {data!r}"))
                else:
                    results.append(ok(sid, slug))
        elif sc["expect"] == "resolve_opus_1m":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run(
                [sys.executable, str(script), "--name", "opus", "--json"],
                capture_output=True,
                text=True,
            )
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                slug = data.get("slug") or ""
                if p.returncode != 0 or data.get("name") != "opus" or "[1m]" not in slug:
                    results.append(fail(sid, f"rc={p.returncode} {data!r}"))
                else:
                    results.append(ok(sid, slug))
        else:
            results.append(fail(sid, f"unknown expect {sc.get('expect')}"))

    types = {}
    for sc, r in zip(EVAL["scenarios"], results):
        if r.get("skipped"):
            continue
        types.setdefault(sc["type"], 0)
        if r["ok"]:
            types[sc["type"]] += 1
    mins = EVAL.get("min_scenarios", {})
    for k, n in mins.items():
        if types.get(k, 0) < n:
            results.append(fail(f"min-{k}", f"need {n} passing {k}, got {types.get(k, 0)}"))

    if (ROOT / "ko").exists():
        results.append(fail("no-nested-locale", "ko/ folder belongs on branch ko, not this checkout"))

    failed = [r for r in results if not r["ok"]]
    print(json.dumps({"version": version, "locale": EVAL["locale"], "results": results, "failed": len(failed)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
