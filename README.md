# orchestrator-consultant-gate

Get an independent, read-only second opinion before you score, merge, ship, or make a large change—without changing the agent running your session.

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

One AI writes the **plan**. **GATE** before work. The other AI **reviews** it read-only. Notes go back. Same session.

The consult child is a different model from the executor. Default family is `fable` → `claude-fable-5`. This turn, pick another with `--name grok`, `--name gpt`, or `--name gemini`. Blocked spawn → `fallback_slug` in the same `--json`.

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

Not in `host-skills` catalog. Optional: `agent-model-registry set fable <id>`.
