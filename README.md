# opus-fable-orchestrator-ko

Opus가 실행하고, Fable이 게이트와 과신 신호에서 읽기 전용으로 자문한다.

## 스킬 에디션

로케일마다 **git 브랜치**가 하나다. 쓸 언어 브랜치를 설치한다.

| 에디션 | 브랜치 | 설치 |
|---|---|---|
| English | [`main`](https://github.com/dalsoop/opus-fable-orchestrator/tree/main) | `npx skills add dalsoop/opus-fable-orchestrator -g -y` |
| 한국어 | [`ko`](https://github.com/dalsoop/opus-fable-orchestrator/tree/ko) | `npx skills add dalsoop/opus-fable-orchestrator#ko -g -y` |

지금 보고 있는 것은 **한국어 (`ko`)** 이다. `owner/repo@이름`은 스킬 이름이고, 브랜치는 `owner/repo#ko`다.

**부모:** `/model` + `agent-model-registry get claude` (호스트가 쓰면 `[1m]`). 자문은 부모가 아님. **Opus 5.0 부모 금지.**

```bash
npx skills add dalsoop/opus-fable-orchestrator#ko -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
```

자문 기본값: `agent-model-registry set fable <id>`. GUI: `agent-model-registry open`. 설치 목록: `agent-skills open`.

<p align="center">
  <img src="assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`eval/`](eval/) · MIT

---

# 에이전트 전용

사람은 여기 위에서 멈춰도 된다. 정본은 [`SKILL.md`](SKILL.md).

1. **부모:** `/model` + `agent-model-registry get claude` (호스트가 쓰면 `[1m]`). 자문은 부모가 아님. Opus 5.0 / `opus-5` 부모 거부.
2. **자문 id:** `agent-model-registry get fable` → 이 호스트 Task 허용 목록에 매핑. 이번 턴 사용자 지정 또는 `set fable <id>`.
3. **필수 자문:** 점수 보고 전, 10파일 이상 수정 전, 머지/배포 전. 과신 신호 2개 이상이면 강제.
4. grep·파일읽기·기계적 수정·명확한 버그수정에는 부르지 않는다.
5. 브리핑 `templates/fable-briefing.md`. 소화 `templates/digest.md`. 읽기 전용. Timeout이면 진행하고 다음 게이트에서 재시도.

