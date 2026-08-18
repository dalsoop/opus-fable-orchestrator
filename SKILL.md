---
name: opus-fable-orchestrator-ko
license: MIT
compatibility: Cursor Task Fable (claude-fable-5-thinking-high) 또는 허용 목록의 다른 자문 slug.
metadata:
  author: dalsoop
  version: "1.7.0"
  locale: ko
description: >-
  읽기 전용 자문 자식을 연다(기본은 Cursor Fable). 제품 점수, 전문가 의견, fable 자문,
  페이블 자문, 자문 받아와, 머지/배포 전에 쓴다. 점수 보고 전, 10개 이상 파일 수정 전,
  점수가 오르기만 하거나 스스로 100/완료면 선제 적용. grep, 기계적 수정, 명확한 버그수정은 건너뛴다.
---

# Opus-Fable Orchestrator (한국어)

부모는 세션 모델. 부모를 Opus 5.0으로 바꾸지 않는다. 자문은 읽기 전용 자식(파일·도구 없음).

## 자문

**필수** — 점수 보고 전, 10개 이상 파일 수정 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성", diff 밖 증거 없음, 같은 에이전트가 작성·채점.

**하지 않음:** grep, 파일 읽기, 기계적 수정, 명확한 버그 수정.

응답 ≤500단어. 매 턴 금지. 실행자를 자문으로 대체하지 않음.

## 호출

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
```

`--json` → `{registry, slug, name}`. Task `model`은 `slug`. 이번 턴에 모델을 말했으면 `--name`. 항상 기본값: `agent-model-registry set fable <id>` (없어도 됨. 없으면 `claude-fable-5-thinking-high`).

`templates/fable-briefing.md` (증거 ≠ 해석). 반박 + 닫힌 3–5 + 열린 1: "내가 놓친 카테고리는?" 비밀 금지.

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<resolve-consult.py slug>",
  prompt: <브리핑>
})
```

Claude Code: `Agent({ model: "<slug>", ... })`. 도구 호출 지시 → reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`.

**완료:** 모든 항목이 accept / reject / defer + 이유, 보고가 `min(코드 점수, 도달 가능 상한)`, 사용자에게 `registry` + `slug`를 말함.

상한은 외부. 코드로 올리지 않음.
