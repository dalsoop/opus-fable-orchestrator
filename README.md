# opus-fable-orchestrator-ko

Opus가 실행하고, Fable이 게이트와 과신 신호에서 읽기 전용으로 자문한다.

## 스킬 에디션

로케일마다 **git 브랜치**가 하나다. 쓸 언어 브랜치를 설치한다.

| 에디션 | 브랜치 | 설치 |
|---|---|---|
| English | [`main`](https://github.com/dalsoop/opus-fable-orchestrator/tree/main) | `npx skills add dalsoop/opus-fable-orchestrator -g -y` |
| 한국어 | [`ko`](https://github.com/dalsoop/opus-fable-orchestrator/tree/ko) | `npx skills add dalsoop/opus-fable-orchestrator@ko -g -y` |

지금 보고 있는 것은 **한국어 (`ko`)** 이다.

**부모 모델:** `/model claude-opus-4-6[1m]` — 실행자는 Opus 4.6 1M. Fable은 읽기 전용. **부모로 Opus 5.0을 쓰지 않는다 — 오류율이 높다.**

```bash
npx skills add dalsoop/opus-fable-orchestrator@ko -g -y
python3 eval/run.py
```

<p align="center">
  <img src="assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`eval/`](eval/) · MIT
