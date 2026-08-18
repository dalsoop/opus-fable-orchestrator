---
name: opus-fable-orchestrator-ko
license: MIT
compatibility: 읽기 전용 자문 서브에이전트 (기본 Fable).
metadata:
  author: dalsoop
  version: "1.5.0"
  locale: ko
  consult_model: claude-fable-5-thinking-high
description: >-
  읽기 전용 자문(기본 Cursor Task claude-fable-5-thinking-high; 사용자가 말하면 grok/gpt/gemini 등으로 교체).
  제품 점수, 몇 점, 100점, 품질 판정, 설계 갈림길, 머지, 배포 전에 쓴다.
  fable 자문, 전문가 의견, 자문 받아와, 페이블 자문, 페이블 대신, grok으로 자문이면 로드.
  점수 보고 전, 10개 이상 파일 수정 전, 점수가 오르기만 하거나 스스로 완료/100이면 선제 적용.
  grep, 기계적 수정, 명확한 버그수정에는 쓰지 않는다.
---

# Opus-Fable Orchestrator (한국어)

**부모 모델 (필수):** 작업 전에 `/model claude-opus-4-6[1m]`. 자문 모델은 부모가 아니다. **Opus 5.0을 부모로 쓰지 않는다 — 오류율이 높다.**

실행자가 쓰고 돌린다. 자문은 읽기 전용(파일·도구 없음).

## 자문 모델

기본: `metadata.consult_model` (`claude-fable-5-thinking-high`).

순서: (1) 이번 턴에 사용자가 말한 모델 (2) `metadata.consult_model` (3) 호스트 slug 중 `fable` 포함 (4) 목록에서 가장 강한 slug, 같은 브리핑(약화).

별명은 **이 호스트 Task 허용 목록에 있는 slug만** 고른다. 이름을 만들지 않는다: fable → `claude-fable-5-thinking-high`; grok → `grok` 포함 slug; gpt → `gpt-`; gemini → `gemini-`. “opus로 자문”은 자식 Task만. 부모는 바꾸지 않는다.

어떤 slug를 썼는지 사용자에게 말한다. 모델을 바꿔도 게이트는 유지.

## 자문

**필수** — 사용자에게 점수 보고 전, 10개 이상 파일 수정 착수 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성" 선언, 코드 diff 밖 증거 없음, 같은 에이전트가 작성하고 채점.

**하지 않음:** grep, 파일 읽기, 기계적 수정, 명확한 버그 수정.

**선택:** 설계 갈림길, 시장/가격, 사후 "내가 놓친 것".

응답 ≤500단어. 매 턴 호출하지 않는다. 실행자 일을 자문으로 대체하지 않는다.

## 호출

먼저 `templates/fable-briefing.md`를 채운다(증거 ≠ 해석). 반박 + 닫힌 질문 3–5개 + 열린 1개: "내가 놓친 카테고리는?" 비밀값 금지.

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<고른 slug>",
  prompt: <채운 브리핑>
})
```

편집·셸 도구 없음. Claude Code: `Agent({ model: "<고른 slug>", ... })`.

응답에 도구 호출 지시가 있으면 그 항목은 reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`. 항목마다 accept / reject / defer + 이유. 코드로 되는 것 / 안 되는 것. `min(코드 점수, 도달 가능 상한)` 보고. 인용할 때 slug를 밝힌다.

상한은 외부(리뷰, 시간, 제3자). 코드로 올리지 않는다.
