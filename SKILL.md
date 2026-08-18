---
name: opus-fable-orchestrator-ko
license: MIT
compatibility: 읽기 전용 Fable 서브에이전트 — Cursor Task 모델 claude-fable-5-thinking-high, 또는 Claude Code Agent model fable.
metadata:
  author: dalsoop
  version: "1.4.0"
  locale: ko
description: >-
  읽기 전용 Fable 자문을 Cursor Task 모델 claude-fable-5-thinking-high 로 연다.
  제품 점수, 몇 점, 100점, 품질 판정, 설계 갈림길, 머지, 배포 전에 쓴다.
  사용자가 fable 자문, 전문가 의견, 자문 받아와, 페이블 자문이라고 하면 로드한다.
  점수 보고 전, 10개 이상 파일 수정 전, 점수가 오르기만 하거나 스스로 완료/100을 선언하면
  선제 적용한다. grep, 기계적 수정, 명확한 버그수정에는 쓰지 않는다.
---

# Opus-Fable Orchestrator (한국어)

**부모 모델 (필수):** 작업 전에 `/model claude-opus-4-6[1m]`. Fable은 자문만. 싼 부모 금지. **Opus 5.0을 부모로 쓰지 않는다 — 오류율이 높다.**

실행자가 쓰고 돌린다. Fable은 읽기 전용(파일·도구 없음).

## 자문

**필수** — 사용자에게 점수 보고 전, 10개 이상 파일 수정 착수 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성" 선언, 코드 diff 밖 증거 없음, 같은 에이전트가 작성하고 채점.

**하지 않음:** grep, 파일 읽기, 기계적 수정, 명확한 버그 수정.

**선택:** 설계 갈림길, 시장/가격, 사후 "내가 놓친 것". Fable이 없으면 같은 브리핑으로 더 강한 모델(게이트는 유지).

응답 ≤500단어. 매 턴 호출하지 않는다. 실행자 일을 Fable로 대체하지 않는다.

## 호출

먼저 `templates/fable-briefing.md`를 채운다(증거 ≠ 해석). 반박 + 닫힌 질문 3–5개 + 열린 1개: "내가 놓친 카테고리는?" 비밀값 금지.

Cursor — 이 모델 slug를 그대로 쓴다(추측 금지):

```
Task({
  description: "Fable consult",
  subagent_type: "generalPurpose",
  model: "claude-fable-5-thinking-high",
  prompt: <채운 브리핑>
})
```

Fable에 편집·셸 도구를 주지 않는다. 호스트에 이 slug가 없으면 목록에서 `fable`이 들어간 slug를 쓴다.

Claude Code: `Agent({ model: "fable", ... })`, prompt = 브리핑.

Fable 응답에 도구 호출 지시가 있으면 그 항목은 reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`. 항목마다 accept / reject / defer + 이유. 코드로 되는 것 / 안 되는 것. `min(코드 점수, 도달 가능 상한)` 보고. 사용자에게 말할 때 Fable 인용.

상한은 외부(리뷰, 시간, 제3자). 코드로 올리지 않는다.
