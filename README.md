# orchestrator-consultant-gate

Before orchestration, critic the execution document (the plan and any child prompts) with read-only Fable. The session agent does not switch. The consult costs tokens and is not ground truth.

English (`main`). Korean: branch [`ko`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/ko).

```bash
npx skills add dalsoop/orchestrator-consultant-gate -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py   # host spawn; skips if Cursor workspace trust blocks
```

`npx` copies **files**. A second opinion needs the **host** to spawn a child. That is not E2E from install.

Korean: `npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-en.png" alt="One AI writes the plan. Another AI reviews it." width="920">
</p>

One AI writes the **execution document** from the work order. **GATE** before orchestration and before audit-then-change. Fable **rebuts** it read-only: one more missed bottleneck, a hole in a child prompt, an omitted category. Notes go back. Same session. Claims are probabilistic. Digest them. Do not treat them as answers.

The critic is Fable (`fable` → `claude-fable-5`). This turn, override with `--name grok`, `--name gpt`, or `--name gemini`. Blocked spawn → `fallback_slug` in the same `--json`. Hosts: Cursor, Claude Code, Codex, Grok TUI (`GROK_AGENT=1`). The session agent fills `templates/` at the gate.

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

Score a `SKILL.md`: `npx skills add dalsoop/skill-audit -g -y`

Not in `host-skills` catalog. Optional: `agent-model-registry set fable <id>`.
