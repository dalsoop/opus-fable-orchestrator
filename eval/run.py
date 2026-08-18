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
    desc = fm.get("description", "")
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
        elif sc["expect"] == "skill_requires_opus_parent":
            if "agent-model-registry get claude" not in skill_text or "5.0" not in skill_text:
                results.append(fail(sid, "parent must use registry get claude and refuse 5.0"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "registry_get_fable":
            import shutil
            import subprocess

            bin_ = shutil.which("agent-model-registry")
            if not bin_:
                results.append(fail(sid, "agent-model-registry not on PATH"))
            else:
                p = subprocess.run([bin_, "get", "fable"], capture_output=True, text=True)
                out = (p.stdout or "").strip()
                if p.returncode != 0 or not out:
                    results.append(fail(sid, f"get fable failed rc={p.returncode} {out!r}"))
                else:
                    results.append(ok(sid, out.splitlines()[-1]))
        elif sc["expect"] == "folder_matches_skill_name":
            if ROOT.name != EVAL["skill"]:
                results.append(fail(sid, f"folder {ROOT.name!r} != name {EVAL['skill']!r}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "skill_contains_fable_slug":
            slug = EVAL.get("fable_model_slug", "")
            if slug not in skill_text:
                results.append(fail(sid, f"SKILL.md missing Task slug {slug!r}"))
            else:
                results.append(ok(sid))
        elif sc["expect"] == "skill_allows_consult_override":
            miss = [n for n in EVAL.get("override_needles", []) if n not in skill_text]
            results.append(fail(sid, f"missing={miss}") if miss else ok(sid))
        elif sc.get("harness") == "live":
            results.append(fail(sid, "live harness not implemented in run.py"))
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
