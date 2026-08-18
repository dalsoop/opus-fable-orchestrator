---
name: orchestrator-consultant-gate-ko
license: MIT
compatibility: 읽기 전용 자식을 띄울 수 있는 호스트(Cursor Task, Claude Code Agent, Codex, …). slug는 호스트 고유(resolve-consult.py).
metadata:
  author: dalsoop
  version: "1.9.1"
  locale: ko
description: >-
  오케스트레이션하는 에이전트를 위한 컨설턴트 게이트. 읽기 전용 자문 자식을 연다(기본은
  Fable 계열). 컨설턴트 게이트, 전문가 의견, fable 자문, 페이블 자문, 자문 받아와,
  머지/배포 전에 쓴다. 점수 보고 전, 10개 이상 파일 수정 전, 점수가 오르기만 하거나
  스스로 100/완료면 선제 적용. grep, 기계적 수정, 명확한 버그수정은 건너뛴다.
---

# Orchestrator Consultant Gate (한국어)

당신이 오케스트레이터다: 이미 이 세션을 돌리는 모델(Grok, Codex, Claude, GPT, …). 부모를 바꾸지 않는다. 게이트에서 읽기 전용 컨설턴트 자식(파일·도구 없음). 자문이 실행자를 대체하지 않는다.

## 게이트

**필수** — 점수 보고 전, 10개 이상 파일 수정 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성", diff 밖 증거 없음, 같은 에이전트가 작성·채점.

**하지 않음:** grep, 파일 읽기, 기계적 수정, 명확한 버그 수정.

응답 ≤500단어. 매 턴 금지.

## 호출

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
```

`--json` → `{host, registry, slug, name}`. `host`는 이번 세션(`CONSULT_HOST`: cursor|claude|codex). `slug`는 그 호스트 자식 API용. 기본 계열: `agent-model-registry get fable` → `claude-fable-5`. Cursor만 Task slug로 매핑. Claude Code·Codex는 계열 id를 그대로. Claude/Codex에서 `cursor --list-models`를 부르지 말 것.

이번 턴에 자문 모델을 말했으면 `--name`.

`templates/fable-briefing.md` (증거 ≠ 해석). 반박 + 닫힌 3–5 + 열린 1: "내가 놓친 카테고리는?" 비밀 금지.

Cursor:

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<slug>",
  prompt: <브리핑>
})
```

Claude Code: `Agent({ model: "<slug>", ... })`. Codex: 호스트가 되면 `-m <slug>`로 자식. 도구 호출 지시 → reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`.

**완료:** 모든 항목이 accept / reject / defer + 이유, 보고가 `min(코드 점수, 도달 가능 상한)`, 사용자에게 `host` + `registry` + `slug`를 말함.

상한은 외부. 코드로 올리지 않음.
