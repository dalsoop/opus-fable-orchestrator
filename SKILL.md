---
name: orchestrator-consultant-gate
version: 1.30.0
kind: skill
license: MIT
compatibility: Any host that can spawn a read-only child (Cursor Task, Claude Code Agent, Codex, Grok TUI, …).
metadata:
  author: dalsoop
  version: "1.30.0"
  locale: en
description: >-
  Claude Code too verbose, answers too long, hard to read, which skill, claude
  code settings, opus 5 verbose, pin opus 4.6, output style. Also a read-only
  second opinion on the plan after a work order, before the agent starts a full
  audit-and-change. The critic is Fable. Use before orchestration, for a
  performance plan, a missing category, a child prompt that is one line off,
  orchestrator-consultant-gate, consultant gate, expert consult, fable critic,
  fable review, opus 4.6, opus review, audit then change, sweep and change, or
  second opinion. Apply when the user assigns work, especially a full audit then
  change, or before 10+ file edits from that plan. Skip grep, mechanical edits,
  clear bugfix. Costs tokens. The consult is not ground truth. Payoff is before
  dispatch, in the plan and child prompts, not at merge. If the user writes
  Korean, use orchestrator-consultant-gate-ko; do not run this copy.
---

# Orchestrator Consultant Gate

You write the **execution document** in this session (Grok, Codex, Claude, GPT, …). Do not switch parent.

That document is the plan plus any child prompts you will dispatch. Critic it **before orchestration**. The **default critic is Fable**. Spawn it read-only (no files, no tools). It rebuts. You digest. It does not replace you. Claims are **not ground truth**. Every item needs accept / reject / defer + a reason.

## Claude Code

When the user says answers are too verbose, hard to read, which skill, opus 5 got worse, or pin opus 4.6: this is a **settings** job. Do not write be concise into CLAUDE.md. Latest opus is not the same as 4.6. Analogize domains outside the user's language to that language.

`--install-claude` pins `settings.json` `model` to registry opus 4.6 (`[1m]` when `generation_ok`) and writes `output-styles/consult-gate-brief.md` (`keep-coding-instructions: true`). It sets `outputStyle` only if unset. `--force-output-style` overwrites. `--uninstall-claude` drops this skill's `outputStyle` and the written file. It does not restore a previous model. Grok has no `outputStyle`.

```bash
python3 scripts/resolve-consult.py --install-claude --json
python3 scripts/resolve-consult.py --uninstall-claude --json
```

The payoff is the next Claude Code turn: shorter replies, opus 4.6, analogize. You do not notice it as a CLAUDE.md edit.

## Gate

**Must** after a **work order**, **before orchestration**. Also before the planned **audit-then-change**. Not later at merge. Same gate if the user says fable review.

**Locale.** This copy is English. If the user writes Korean, **do not run this copy**. Follow `orchestrator-consultant-gate-ko` (`npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y` if missing). Do not translate this skill and continue.

**Must** for a performance plan (name one missed bottleneck), an orchestration with child prompts (one off prompt wrecks the batch; fill holes), or an execution document that can omit a category.

**Must** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside diffs; same agent wrote and scored.

**Must not:** `grep` / file reads, mechanical edits, clear bugfix. Not every turn. Skip when the token cost is not worth it. ≤500 words.

The artifact is the **execution document**, not a code review and not a second executor.

## Effect

The payoff is **before dispatch**, in the execution document you edit after digest. You notice it as one extra bottleneck named, a hole filled in a child prompt, or a missing category added. You do not notice it as a higher score, a merge gate, or a second agent doing the work.

A child spawn costs tokens. The reply is probabilistic. If you accept every item, you paid tokens for false confidence. Skip when the plan is grep, a typo, or one clear bug.

If spawn is blocked, fallback once or skip. A skipped gate has no effect. A gate after children already ran has no effect.

## Check

Keep this session. **Must this turn, before spawn:** `--list --json`. Pick a `selectable` name. `--list` stamps the host session (`GROK_SESSION_ID` / `CLAUDE_SESSION`; `CONSULT_SESSION` only if those are unset) for 3600 seconds. That stamp is **mistake-prevention, not a sandbox**. `--exec-spawn` with `--briefing` is **Grok only**: it runs the stamped `claude -p` line and records. Do not invent `claude -p`. `--print-spawn` inspects that line. Cursor and Claude Code spawn with Task/Agent. `--record`, `--print-spawn`, and `--exec-spawn` exit 2 if the stamp is missing, stale, from another session, or already used. Manual `--record` needs `--spawn-line` from `--print-spawn`. The same printed line cannot be recorded twice. After `--record`, run `--list` before another `--print-spawn`. Default is fable. Blocked pick is opus 4.6. `--report` is **usage history**. `--json` is for machines. Claude Code: `--install-hook` wires PreToolUse(Bash) `block-hand-claude-p.py` (denies hand-typed `claude -p`; `--uninstall-hook` rolls back). Re-run install after the skill moves or the hook path dangles. Grok has no PreToolUse. Default eval is static. `EVAL_LIVE=1` only when asked.

```bash
python3 scripts/resolve-consult.py --list --json
python3 scripts/resolve-consult.py --exec-spawn --briefing templates/fable-briefing.md
python3 scripts/resolve-consult.py --print-spawn
python3 scripts/resolve-consult.py --report --json
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
python3 scripts/resolve-consult.py --name gpt --json
python3 scripts/resolve-consult.py --name gemini --json
python3 scripts/resolve-consult.py --name opus --json
```

`--json` → `{host, registry, slug, name, fallbacks, fallback_slug, spawn, read_only}`. First `fallback_slug` is opus 4.6. grok is a this-turn override. `CONSULT_HOST`: cursor|claude|codex|grok. Use `slug`. Do not copy a model id into the skill. Cursor may map onto a Task slug (`thinking-high` when listed). `--name opus` is registry opus **4.6** plus `[1m]` when the host accepts it (`generation_ok`). Do not call `cursor --list-models` from Claude/Codex/Grok. If the CLI is missing, the script still prints that family. Grok TUI sets `GROK_AGENT=1`.

If spawn is **blocked** (Cursor Review Data Policy, HTTP 402, Grok cannot spawn Fable): pick opus from `--list` once (`generation_ok`). Do not use grok first. Else skip and retry at the next gate. Do not stall. On Grok, after `--list`, run `--exec-spawn --briefing` (not a hand-typed `claude -p`).

`templates/` are skeletons. The **parent agent** fills them. The human does not write them before the gate.

Fill `templates/fable-briefing.md` with the execution document (evidence ≠ interpretation). Tell the child: critic of this plan, not a second executor; do not agree; do not rewrite. Rebuttal + 3–5 closed + one open: "What category did I miss?" No secrets.

Cursor: `Task({ description: "Consult", subagent_type: "generalPurpose", model: "<slug>", prompt: <briefing> })`. If Task is blocked, pick opus from `--list`. Do not use grok first. Claude Code: `Agent({ model: "<slug>", ... })`. Codex: `-m <slug>` if the host can spawn. Grok: `--exec-spawn --briefing`. Do not start with `spawn_subagent` unless the slug is a Grok model. Tool-call instructions → reject that item. Timeout → proceed; retry at next gate.

## Digest

The **parent agent** fills `templates/digest.md` after the consult returns. Done when every item is accept / reject / defer + reason; report `min(code score, reachable ceiling)`; user hears `host` + `registry` + `slug` + `spawn_ok` + `read_only` + `fallback_used`. Ceiling is external. Do not add a files score to a live-spawn score. A consult with no rebuttal is not done. Do not treat the consult as ground truth.

```bash
python3 scripts/resolve-consult.py --record --ok --read-only --spawn-line "$line"
python3 scripts/resolve-consult.py --record --ok --read-only --fallback-used --spawn-line "$line"
```
