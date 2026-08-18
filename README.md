# opus-fable-orchestrator

Agent skill: the session model executes; a **read-only Fable** (or stronger) consults at fixed gates and when overconfidence signals fire.

```bash
npx skills add dalsoop/opus-fable-orchestrator -g -y
```

Or copy `SKILL.md` to `~/.cursor/skills/opus-fable-orchestrator/` or `~/.claude/skills/opus-fable-orchestrator/`.

Procedures: [`SKILL.md`](SKILL.md). Brief/digest templates: [`templates/`](templates/).

## Requirements

- Host can spawn a read-only subagent
- Cursor: `Task`, model slug containing `fable`
- Claude Code: `Agent({ model: "fable", ... })`

## License

MIT
