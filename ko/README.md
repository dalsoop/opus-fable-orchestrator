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
