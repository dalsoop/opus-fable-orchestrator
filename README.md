# opus-fable-orchestrator

Opus executes. Fable advises read-only at gates and on overconfidence signals.

## Skill editions

Each locale is a **git branch**. Install the branch you want.

| Edition | Branch | Install |
|---|---|---|
| English | [`main`](https://github.com/dalsoop/opus-fable-orchestrator/tree/main) | `npx skills add dalsoop/opus-fable-orchestrator -g -y` |
| Korean | [`ko`](https://github.com/dalsoop/opus-fable-orchestrator/tree/ko) | `npx skills add dalsoop/opus-fable-orchestrator#ko -g -y` |

You are on **English (`main`)**. `owner/repo@name` is a **skill name**, not a git branch. Korean checkout is `owner/repo#ko`.

**Parent:** `/model` from `agent-model-registry get claude` (keep `[1m]` if the host uses it). Consult is not the parent. **Do not use Opus 5.0 as parent.**

```bash
npx skills add dalsoop/opus-fable-orchestrator -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
```

Change the consult default: `agent-model-registry set fable <id>`. GUI: `agent-model-registry open`. Installed skills: `agent-skills open`.

<p align="center"><strong>English</strong></p>
<p align="center">
  <img src="assets/how-opus-fable-works-en.png" alt="How Opus–Fable works" width="920">
</p>

<p align="center"><strong>한국어</strong></p>
<p align="center">
  <img src="assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`eval/`](eval/) · MIT

---

# For agents

Humans can stop above. Prefer [`SKILL.md`](SKILL.md) if both are loaded.

1. **Parent:** `/model` from `agent-model-registry get claude` (keep `[1m]` if the host uses it). Consult is not the parent. Refuse `opus-5` / Opus 5.0 as parent.
2. **Consult id:** `agent-model-registry get fable`, then map onto this host’s Task allowlist. User can override this turn or `set fable <id>`.
3. **Must consult** before reporting a score; starting 10+ file edits; merge/ship. **Must** if 2+ of: scores only rose; self-declared 100 / "done"; no evidence outside diffs; maker=checker.
4. **Must not** for grep, file reads, mechanical edits, clear bugfix.
5. Brief `templates/fable-briefing.md`. Digest `templates/digest.md`. Read-only spawn. Timeout → proceed; retry at next gate.

