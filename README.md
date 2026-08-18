# opus-fable-orchestrator

Opus executes. Fable advises. A **circuit breaker** forces consultation when the executor overestimates itself.

> The dangerous moment is not “when should I ask Fable?” — it is “when the runner decides not to.”

<p align="center">
  <img src="assets/how-opus-fable-works-en.png" alt="How Opus–Fable works" width="920">
</p>

<details>
<summary>한국어 다이어그램</summary>
<p align="center">
  <img src="assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>
</details>

Agent skill for [Cursor](https://cursor.com), [Claude Code](https://claude.ai/code), and similar hosts that can spawn a Fable (or equivalent) subagent.

```bash
npx skills add dalsoop/opus-fable-orchestrator -g -y
```

Or copy `SKILL.md` into `~/.cursor/skills/opus-fable-orchestrator/` / `~/.claude/skills/opus-fable-orchestrator/`.

## How it runs

Clockwise loop: **Opus executes → gates → force consult → Fable advises → briefing v2 → digest → reachable ceiling → back to Opus**.

- **Gates (mandatory):** before publishing a score, before a 10+ file change, before merge/ship.
- **Circuit breaker:** 2+ of monotone scores, perfect-score claim, code-only loop, maker=checker → force Fable.
- **Fable is read-only.** It talks. It does not edit files.
- **Digest** is accept / reject / defer. Treating Fable as gospel is also bias.

Full procedure: [`SKILL.md`](SKILL.md). Templates: [`templates/fable-briefing.md`](templates/fable-briefing.md), [`templates/digest.md`](templates/digest.md).

## Requirements

- A host that can spawn a **read-only** Fable (or stronger) subagent
- Cursor: `Task` with a model slug containing `fable`
- Claude Code: `Agent({ model: "fable", ... })`

## License

MIT
