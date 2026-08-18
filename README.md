# orchestrator-consultant-gate

Get an independent, read-only second opinion before you score, merge, ship, or make a large change—without changing the agent running your session.

English (`main`). Korean: branch [`ko`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/ko).

```bash
npx skills add dalsoop/orchestrator-consultant-gate -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py   # host roundtrip; skips if Cursor workspace trust blocks
```

Korean: `npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y`

### Optional models

Keep the session agent if one is already running. If you are picking models:

| Role | Model | Value |
|---|---|---|
| Executor | **Opus 4.6** (not Opus 5.0) | Best cost for writing and running. 5.0 is the wrong parent for this skill. |
| Consult | **Fable 5** | Best cost for a short, read-only second opinion. Too expensive as the executor. |

<p align="center">
  <img src="assets/how-the-gate-works-en.png" alt="Session model stays; optional Opus 4.6 executor and Fable 5 consult" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

Not in `host-skills` catalog. Optional: `agent-model-registry set fable <id>`.
