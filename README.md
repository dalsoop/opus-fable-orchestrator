# orchestrator-consultant-gate

Consultant gate for the orchestrating agent. Session model stays. Read-only child at score/merge gates.

English (`main`). Korean: branch [`ko`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/ko).

```bash
npx skills add dalsoop/orchestrator-consultant-gate -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py   # roundtrip on this host (cursor or claude)
```

Korean: `npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-en.png" alt="Orchestrator consultant gate" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

Not in `host-skills` catalog. Optional: `agent-model-registry set fable <id>`.
