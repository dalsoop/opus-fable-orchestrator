# opus-fable-orchestrator

Opus executes. Fable advises. A **circuit breaker** forces consultation when the executor overestimates itself.

> The dangerous moment is not “when should I ask Fable?” — it is “when the runner decides not to.”

Agent skill for [Cursor](https://cursor.com), [Claude Code](https://claude.ai/code), and similar hosts that can spawn a Fable (or equivalent) subagent.

Install:

```bash
npx skills add dalsoop/opus-fable-orchestrator -g -y
```

Or copy `SKILL.md` into `~/.cursor/skills/opus-fable-orchestrator/` / `~/.claude/skills/opus-fable-orchestrator/`.

## Why

Fable is expensive. Calling it every turn is waste. Skipping it before irreversible decisions is more expensive.

The executor often **does not know it is overconfident**. In the session that produced this skill, Opus declared 100/100. Fable scored 42. The 58-point gap was not closable by more code.

This skill makes consultation **mandatory at gates** and **automatic when overconfidence signals fire** — not a courtesy the runner can skip.

## Killer feature: circuit breaker

Four behavioral signals (not self-report):

| # | Signal | Detection |
|---|--------|-----------|
| 1 | Monotone scores | Score only goes up |
| 2 | Perfect score | “100”, “done”, “complete” |
| 3 | Code-only loop | Fixes and re-scores on diffs; zero external evidence |
| 4 | Maker = checker | Same agent writes and grades |

**2+ signals → force a Fable consult.**

Plus fixed gates: before publishing a score, before a 10+ file change, before merge/ship.

## Briefing protocol (v2)

Do not ask “what do you think?” Separate evidence from interpretation, **invite rebuttal**, and always include one open question: *what category did I miss?*

Template: [`templates/fable-briefing.md`](templates/fable-briefing.md)

Digest Fable’s answer with accept / reject / defer — authority anchoring is also bias. Template: [`templates/digest.md`](templates/digest.md)

## Requirements

- A host that can spawn a **read-only** Fable (or stronger) subagent
- Cursor: `Task` with a model slug containing `fable`
- Claude Code: `Agent({ model: "fable", ... })`

Fable talks. It does not edit files or run tools. The parent model remains the executor.

## License

MIT
