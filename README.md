# opus-fable-orchestrator

**Required — set the parent model first. This is the point of the skill.**

```text
/model claude-opus-4-6[1m]
```

Opus 4.6 (1M context) is the executor. Fable is only the read-only consultant. Do not run this skill with a cheaper session model.

English skill. Session model executes. Read-only Fable consults at gates and on overconfidence signals.

Korean skill: [`ko/`](ko/) (`opus-fable-orchestrator-ko`).

```bash
npx skills add dalsoop/opus-fable-orchestrator -g -y
```

Korean install: copy `ko/` to `~/.cursor/skills/opus-fable-orchestrator-ko/` (or `~/.claude/skills/`).

<p align="center">
  <img src="assets/how-opus-fable-works-en.png" alt="How Opus–Fable works" width="920">
</p>

Procedure: [`SKILL.md`](SKILL.md). Templates: [`templates/`](templates/).

Cursor: `Task`, model slug containing `fable`. Claude Code: `Agent({ model: "fable", ... })`.

MIT

---

# For agents

Humans can stop above.

1. **Before any work:** `/model claude-opus-4-6[1m]`. Parent = Opus 4.6 1M. If the session is not that model, switch, then continue. Do not execute this skill as Sonnet/Haiku/Grok.
2. Prefer [`SKILL.md`](SKILL.md) if both are loaded. Do not invent extra stages.
3. Fable = read-only advisor (no files, no tools). Spawn with a model slug containing `fable`.
4. **Must consult** before reporting a score; starting 10+ file edits; merge/ship. **Must consult** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside code diffs; same agent wrote and scored.
5. **Must not consult** for grep, file reads, mechanical edits, clear bugfix.
6. Brief: `templates/fable-briefing.md`. Digest: `templates/digest.md`.
