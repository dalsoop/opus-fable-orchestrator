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
                        elif (data.get("fallbacks") or [{}])[0].get("name") != "opus":
                            results.append(fail(sid, f"first fallback not opus: {data.get('fallbacks')!r}"))
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
            miss = [n for n in ("--name grok", "--name gpt", "--name gemini", "--name opus", "--list", "--report") if n not in skill_text]
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
        elif sc["expect"] == "consult_list":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--list", "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                critics = {c.get("name"): c for c in data.get("critics") or []}
                opus = critics.get("opus") or {}
                if "fable" not in critics or "opus" not in critics:
                    results.append(fail(sid, f"names={list(critics)}"))
                elif not opus.get("generation_ok") or opus.get("generation") != "opus-4-6":
                    results.append(fail(sid, f"opus {opus!r}"))
                else:
                    results.append(ok(sid, ",".join(critics)))
        elif sc["expect"] == "locale_sibling_list":
            import subprocess

            loc = EVAL.get("locale")
            other = ROOT.parent / (
                "orchestrator-consultant-gate-ko" if loc == "en" else "orchestrator-consultant-gate"
            )
            other_script = other / "scripts" / "resolve-consult.py"
            if not other_script.is_file():
                results.append({"id": sid, "ok": True, "detail": "skipped (no sibling checkout)", "skipped": True})
            else:
                def _list(script):
                    p = subprocess.run(
                        [sys.executable, str(script), "--list", "--json"],
                        capture_output=True,
                        text=True,
                    )
                    return json.loads(p.stdout)

                try:
                    here = _list(ROOT / "scripts" / "resolve-consult.py")
                    there = _list(other_script)
                except (json.JSONDecodeError, OSError) as e:
                    results.append(fail(sid, str(e)))
                else:
                    def _sig(data):
                        out = []
                        for c in data.get("critics") or []:
                            out.append(
                                (
                                    c.get("name"),
                                    c.get("spawn_first"),
                                    c.get("selectable"),
                                    c.get("gate_default"),
                                    c.get("gate_blocked"),
                                    c.get("generation"),
                                )
                            )
                        return out

                    if _sig(here) != _sig(there):
                        results.append(fail(sid, f"here={_sig(here)} sibling={_sig(there)}"))
                    else:
                        results.append(ok(sid, str(other)))
        elif sc["expect"] == "consult_list_fable_spawn":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--list", "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                fable = next((c for c in data.get("critics") or [] if c.get("name") == "fable"), {})
                first = fable.get("spawn_first")
                if first != "claude -p":
                    results.append(fail(sid, f"fable spawn_first={first!r}"))
                elif fable.get("gate_default") is not True:
                    results.append(fail(sid, f"fable not gate_default: {fable!r}"))
                else:
                    results.append(ok(sid, first))
        elif sc["expect"] == "consult_list_opus_spawn":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--list", "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                opus = next((c for c in data.get("critics") or [] if c.get("name") == "opus"), {})
                first = opus.get("spawn_first")
                if first != "claude -p":
                    results.append(fail(sid, f"opus spawn_first={first!r}"))
                elif opus.get("gate_blocked") is not True:
                    results.append(fail(sid, f"opus not gate_blocked: {opus!r}"))
                elif opus.get("generation") != "opus-4-6" or opus.get("generation_ok") is not True:
                    results.append(fail(sid, f"opus generation {opus!r}"))
                else:
                    results.append(ok(sid, first))
        elif sc["expect"] == "consult_list_unresolved_skip":
            import subprocess

            script = ROOT / "scripts" / "resolve-consult.py"
            p = subprocess.run([sys.executable, str(script), "--list", "--json"], capture_output=True, text=True)
            try:
                data = json.loads(p.stdout)
            except json.JSONDecodeError:
                results.append(fail(sid, f"not json: {p.stdout!r}"))
            else:
                bad = [
                    c.get("name")
                    for c in data.get("critics") or []
                    if c.get("name") in ("gpt", "gemini") and c.get("selectable") is not False
                ]
                results.append(fail(sid, f"still selectable {bad}") if bad else ok(sid))
        elif sc["expect"] == "record_requires_list":
            import subprocess
            import tempfile

            script = ROOT / "scripts" / "resolve-consult.py"
            with tempfile.TemporaryDirectory() as tmp:
                env = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp}
                denied = subprocess.run(
                    [sys.executable, str(script), "--record", "--ok", "--read-only"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                if denied.returncode != 2:
                    results.append(fail(sid, f"no-list rc={denied.returncode} {denied.stderr[-400:]}"))
                else:
                    listed = subprocess.run(
                        [sys.executable, str(script), "--list", "--json"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    printed = subprocess.run(
                        [sys.executable, str(script), "--print-spawn"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    line = (printed.stdout or "").strip()
                    ok_rec = subprocess.run(
                        [sys.executable, str(script), "--record", "--ok", "--read-only", "--spawn-line", line],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    if listed.returncode != 0 or printed.returncode != 0 or ok_rec.returncode != 0:
                        results.append(
                            fail(
                                sid,
                                f"list+print+record rc list={listed.returncode} print={printed.returncode} rec={ok_rec.returncode}",
                            )
                        )
                    else:
                        results.append(ok(sid, "exit 2 then 0"))
        elif sc["expect"] == "print_spawn_requires_list":
            import subprocess
            import tempfile

            script = ROOT / "scripts" / "resolve-consult.py"
            with tempfile.TemporaryDirectory() as tmp:
                env = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp, "CONSULT_SESSION": "eval-print-spawn"}
                denied = subprocess.run(
                    [sys.executable, str(script), "--print-spawn"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                if denied.returncode != 2:
                    results.append(fail(sid, f"no-list rc={denied.returncode} {denied.stderr[-400:]}"))
                else:
                    listed = subprocess.run(
                        [sys.executable, str(script), "--list", "--json"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    printed = subprocess.run(
                        [sys.executable, str(script), "--print-spawn"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    line = (printed.stdout or "").strip()
                    grok_named = subprocess.run(
                        [sys.executable, str(script), "--name", "grok", "--print-spawn"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    if listed.returncode != 0 or printed.returncode != 0:
                        results.append(fail(sid, f"list+print rc list={listed.returncode} print={printed.returncode}"))
                    elif not line.startswith("claude -p --model ") or "--max-turns 1" not in line:
                        results.append(fail(sid, f"bad spawn line {line!r}"))
                    elif grok_named.returncode != 2:
                        results.append(fail(sid, f"grok print-spawn rc={grok_named.returncode}"))
                    else:
                        results.append(ok(sid, line))
        elif sc["expect"] == "list_stamp_session":
            import subprocess
            import tempfile

            script = ROOT / "scripts" / "resolve-consult.py"
            with tempfile.TemporaryDirectory() as tmp:
                env_a = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp, "CONSULT_SESSION": "sess-a"}
                env_b = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp, "CONSULT_SESSION": "sess-b"}
                listed = subprocess.run(
                    [sys.executable, str(script), "--list", "--json"],
                    capture_output=True,
                    text=True,
                    env=env_a,
                )
                other = subprocess.run(
                    [sys.executable, str(script), "--print-spawn"],
                    capture_output=True,
                    text=True,
                    env=env_b,
                )
                same = subprocess.run(
                    [sys.executable, str(script), "--print-spawn"],
                    capture_output=True,
                    text=True,
                    env=env_a,
                )
                if listed.returncode != 0:
                    results.append(fail(sid, f"list rc={listed.returncode}"))
                elif other.returncode != 2:
                    results.append(fail(sid, f"other session rc={other.returncode}"))
                elif same.returncode != 0:
                    results.append(fail(sid, f"same session rc={same.returncode} {same.stderr[-400:]}"))
                else:
                    results.append(ok(sid, "other=2 same=0"))
        elif sc["expect"] == "list_stamp_stale":
            import json as _json
            import subprocess
            import tempfile
            from pathlib import Path as _Path

            script = ROOT / "scripts" / "resolve-consult.py"
            with tempfile.TemporaryDirectory() as tmp:
                env = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp, "CONSULT_SESSION": "eval-stale"}
                listed = subprocess.run(
                    [sys.executable, str(script), "--list", "--json"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                stamp_path = _Path(tmp) / "last-list.json"
                try:
                    stamp = _json.loads(stamp_path.read_text(encoding="utf-8"))
                except (OSError, _json.JSONDecodeError) as e:
                    results.append(fail(sid, f"stamp {e}"))
                else:
                    stamp["ts"] = "2020-01-01T00:00:00Z"
                    stamp_path.write_text(_json.dumps(stamp), encoding="utf-8")
                    stale = subprocess.run(
                        [sys.executable, str(script), "--print-spawn"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    stale_rec = subprocess.run(
                        [sys.executable, str(script), "--record", "--ok", "--read-only"],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    if listed.returncode != 0:
                        results.append(fail(sid, f"list rc={listed.returncode}"))
                    elif stale.returncode != 2 or stale_rec.returncode != 2:
                        results.append(
                            fail(sid, f"stale print={stale.returncode} record={stale_rec.returncode}")
                        )
                    else:
                        results.append(ok(sid, "stale exit 2"))
        elif sc["expect"] == "record_requires_spawn_line":
            import subprocess
            import tempfile

            script = ROOT / "scripts" / "resolve-consult.py"
            with tempfile.TemporaryDirectory() as tmp:
                env = {**os.environ, "ORCHESTRATOR_CONSULT_HOME": tmp, "CONSULT_SESSION": "eval-spawn-line"}
                listed = subprocess.run(
                    [sys.executable, str(script), "--list", "--json"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                missing = subprocess.run(
                    [sys.executable, str(script), "--record", "--ok", "--read-only"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                printed = subprocess.run(
                    [sys.executable, str(script), "--print-spawn"],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                line = (printed.stdout or "").strip()
                wrong = subprocess.run(
                    [
                        sys.executable,
                        str(script),
                        "--record",
                        "--ok",
                        "--read-only",
                        "--spawn-line",
                        "claude -p --model forged --max-turns 1",
                    ],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                ok_rec = subprocess.run(
                    [sys.executable, str(script), "--record", "--ok", "--read-only", "--spawn-line", line],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                if listed.returncode != 0 or printed.returncode != 0:
                    results.append(fail(sid, f"list/print rc {listed.returncode}/{printed.returncode}"))
                elif missing.returncode != 2:
                    results.append(fail(sid, f"no spawn-line rc={missing.returncode}"))
                elif wrong.returncode != 2:
                    results.append(fail(sid, f"forged spawn-line rc={wrong.returncode}"))
                elif ok_rec.returncode != 0:
                    results.append(fail(sid, f"matching spawn-line rc={ok_rec.returncode} {ok_rec.stderr[-400:]}"))
                else:
                    replay = subprocess.run(
                        [sys.executable, str(script), "--record", "--ok", "--read-only", "--spawn-line", line],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    if replay.returncode != 2:
                        results.append(fail(sid, f"replay rc={replay.returncode}"))
                    else:
                        results.append(ok(sid, "missing/wrong/replay=2 match=0"))
        elif sc["expect"] == "locale_shared_procedure":
            needles = EVAL.get("locale_shared_needles") or []
            loc = EVAL.get("locale")
            other = ROOT.parent / (
                "orchestrator-consultant-gate-ko" if loc == "en" else "orchestrator-consultant-gate"
            )
            here = skill_text
            if not needles:
                results.append(fail(sid, "locale_shared_needles empty"))
            elif not (other / "SKILL.md").is_file():
                results.append({"id": sid, "ok": True, "detail": "skipped (no sibling checkout)", "skipped": True})
            else:
                there = (other / "SKILL.md").read_text(encoding="utf-8")
                miss_here = [n for n in needles if n not in here]
                miss_there = [n for n in needles if n not in there]
                if miss_here or miss_there:
                    results.append(fail(sid, f"here={miss_here} sibling={miss_there}"))
                else:
                    results.append(ok(sid, ",".join(needles)))
        elif sc["expect"] == "locale_procedure_order":
            order = EVAL.get("locale_procedure_order") or []
            loc = EVAL.get("locale")
            other = ROOT.parent / (
                "orchestrator-consultant-gate-ko" if loc == "en" else "orchestrator-consultant-gate"
            )

            def _pos(text: str) -> list[int] | str:
                pos = []
                last = -1
                for n in order:
                    i = text.find(n)
                    if i < 0:
                        return n
                    if i <= last:
                        return f"order {n}"
                    pos.append(i)
                    last = i
                return pos

            if not order:
                results.append(fail(sid, "locale_procedure_order empty"))
            elif not (other / "SKILL.md").is_file():
                results.append({"id": sid, "ok": True, "detail": "skipped (no sibling checkout)", "skipped": True})
            else:
                here_pos = _pos(skill_text)
                there_pos = _pos((other / "SKILL.md").read_text(encoding="utf-8"))
                if isinstance(here_pos, str) or isinstance(there_pos, str):
                    results.append(fail(sid, f"here={here_pos} sibling={there_pos}"))
                else:
                    results.append(ok(sid, ",".join(order)))
        elif sc["expect"] == "sibling_script_same":
            import hashlib

            loc = EVAL.get("locale")
            other = ROOT.parent / (
                "orchestrator-consultant-gate-ko" if loc == "en" else "orchestrator-consultant-gate"
            )
            here = ROOT / "scripts" / "resolve-consult.py"
            there = other / "scripts" / "resolve-consult.py"
            if not there.is_file():
                results.append({"id": sid, "ok": True, "detail": "skipped (no sibling checkout)", "skipped": True})
            else:
                a = hashlib.sha256(here.read_bytes()).hexdigest()
                b = hashlib.sha256(there.read_bytes()).hexdigest()
                if a != b:
                    results.append(fail(sid, f"resolve-consult.py drifted {a[:8]} != {b[:8]}"))
                else:
                    results.append(ok(sid, a[:12]))
        elif sc["expect"] == "eval_live_gated":
            src = (ROOT / "eval" / "run.py").read_text(encoding="utf-8")
            if 'sc.get("harness") == "live" and not live' not in src:
                results.append(fail(sid, "live harness not gated on EVAL_LIVE"))
            elif "EVAL_LIVE" not in src:
                results.append(fail(sid, "EVAL_LIVE missing"))
            else:
                results.append(ok(sid))
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
