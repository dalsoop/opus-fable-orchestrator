# opus-fable-orchestrator-ko

Opus가 실행하고, Fable이 게이트와 과신 신호에서 읽기 전용으로 자문한다.

## 스킬 에디션

로케일마다 **git 브랜치**가 하나다. 쓸 언어 브랜치를 설치한다.

| 에디션 | 브랜치 | 설치 |
|---|---|---|
| English | [`main`](https://github.com/dalsoop/opus-fable-orchestrator/tree/main) | `npx skills add dalsoop/opus-fable-orchestrator -g -y` |
| 한국어 | [`ko`](https://github.com/dalsoop/opus-fable-orchestrator/tree/ko) | `npx skills add dalsoop/opus-fable-orchestrator@ko -g -y` |

지금 보고 있는 것은 **한국어 (`ko`)** 이다.

**부모:** `/model` + `agent-model-registry get claude` (호스트가 쓰면 `[1m]`). 자문은 부모가 아님. **Opus 5.0 부모 금지.**

```bash
npx skills add dalsoop/opus-fable-orchestrator@ko -g -y
agent-model-registry get fable
python3 eval/run.py
```

자문 기본값: `agent-model-registry set fable <id>`. GUI: `agent-model-registry open`. 설치 목록: `agent-skills open`.

<p align="center">
  <img src="assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`eval/`](eval/) · MIT
