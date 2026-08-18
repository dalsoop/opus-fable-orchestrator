---
name: opus-fable-orchestrator-ko
license: MIT
compatibility: 읽기 전용 자문 서브에이전트. 자문 id는 agent-model-registry.
metadata:
  author: dalsoop
  version: "1.6.0"
  locale: ko
  consult_model: claude-fable-5-thinking-high
description: >-
  읽기 전용 자문(기본은 agent-model-registry get fable, 호스트 Task 허용 목록에 매핑).
  사용자가 말하면 grok/gpt/gemini로 바꾸거나 agent-model-registry set fable.
  제품 점수, 몇 점, 100점, 품질 판정, 머지, 배포 전.
  fable 자문, 전문가 의견, 자문 받아와, 페이블 자문, 페이블 대신, grok으로 자문이면 로드.
  점수 보고 전, 10개 이상 파일 수정 전, 점수가 오르기만 하거나 스스로 완료/100이면 선제 적용.
  grep, 기계적 수정, 명확한 버그수정에는 쓰지 않는다.
---

# Opus-Fable Orchestrator (한국어)

**부모:** `/model` + `agent-model-registry get claude` (호스트가 쓰면 `[1m]` 유지). 자문은 부모가 아님. 부모 id에 `opus-5` / Opus 5.0이 있으면 거부.

실행자가 쓰고 돌린다. 자문은 읽기 전용.

항상 기본값은 `agent-model-registry` (`~/.agent-models/registry.json`). GUI: `agent-model-registry open`. 설치 목록: `agent-skills open`.

## 자문 모델

```bash
agent-model-registry get fable
agent-model-registry set fable <id>
```

순서: (1) 이번 턴에 사용자가 말한 모델 (2) `agent-model-registry get fable` (3) CLI가 없을 때만 `metadata.consult_model` (4) slug에 `fable` (5) 목록에서 가장 강한 slug.

grok/claude/codex를 말하면 먼저 `agent-model-registry get <name>`.

id를 **이 호스트 Task 허용 목록**에 붙인다: 완전 일치, 접두어(`claude-fable-5` → `claude-fable-5-thinking-high`), 포함. 이름을 만들지 않는다.

레지스트리 id와 Task slug를 사용자에게 말한다. 모델을 바꿔도 게이트는 유지.

## 자문

**필수** — 점수 보고 전, 10개 이상 파일 수정 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성", 코드 diff 밖 증거 없음, 같은 에이전트가 작성·채점.

**하지 않음:** grep, 파일 읽기, 기계적 수정, 명확한 버그 수정.

응답 ≤500단어. 매 턴 호출 금지. 실행자를 자문으로 대체하지 않음.

## 호출

`templates/fable-briefing.md` (증거 ≠ 해석). 반박 + 닫힌 3–5 + 열린 1: "내가 놓친 카테고리는?" 비밀 금지.

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<허용 slug>",
  prompt: <브리핑>
})
```

편집·셸 없음. Claude Code: `Agent({ model: "<resolved>", ... })`.

도구 호출 지시 → 그 항목 reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`. accept / reject / defer + 이유. 코드로 되는 것 / 안 되는 것. `min(코드 점수, 도달 가능 상한)`. 인용 시 레지스트리 id와 slug.

상한은 외부. 코드로 올리지 않음.
