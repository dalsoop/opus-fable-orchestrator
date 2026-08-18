# opus-fable-orchestrator-ko

**필수 — 부모 모델을 먼저 고정한다. 이 스킬의 핵심이다.**

```text
/model claude-opus-4-6[1m]
```

실행자는 Opus 4.6 (1M 컨텍스트). Fable은 읽기 전용 자문만. 싼 세션 모델로 이 스킬을 돌리지 않는다.

영어 스킬: 저장소 루트 [`opus-fable-orchestrator`](../README.md).

이 `ko/` 폴더를 `~/.cursor/skills/opus-fable-orchestrator-ko/` 또는 `~/.claude/skills/`에 복사한다.

<p align="center">
  <img src="../assets/how-opus-fable-works-ko.png" alt="OPUS–FABLE 작동 원리" width="920">
</p>

절차: [`SKILL.md`](SKILL.md). 템플릿: [`templates/`](templates/).

Cursor: `Task`, 모델 slug에 `fable`. Claude Code: `Agent({ model: "fable", ... })`.

MIT

---

# 에이전트 전용

사람은 여기 위에서 멈춰도 된다.

1. **작업 전:** `/model claude-opus-4-6[1m]`. 부모가 Opus 4.6 1M가 아니면 바꾸고 진행. Sonnet/Haiku/Grok으로 이 스킬을 실행하지 않는다.
2. [`SKILL.md`](SKILL.md)가 정본. 단계를 지어내지 않는다.
3. Fable은 읽기 전용. slug에 `fable`이 있는 모델로만 띄운다.
4. **필수 자문:** 점수 보고 전, 10파일 이상 수정 전, 머지/배포 전. 과신 신호 2개 이상이면 강제.
5. grep·파일읽기·기계적 수정·명확한 버그수정에는 부르지 않는다.
6. 브리핑 `templates/fable-briefing.md`. 소화 `templates/digest.md`.
