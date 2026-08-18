---
name: orchestrator-consultant-gate-ko
license: MIT
compatibility: 읽기 전용 하위 에이전트를 띄울 수 있는 호스트(Cursor Task, Claude Code Agent, Codex, …).
metadata:
  author: dalsoop
  version: "1.10.0"
  locale: ko
description: >-
  점수 보고·머지·배포 전에 읽기 전용 전문가 의견을 받는다. 지금 세션 에이전트는 바꾸지
  않는다. 컨설턴트 게이트, 전문가 의견, 자문 받아와, fable 자문, 페이블 자문, 머지/배포 전에 쓴다.
  점수 보고 전, 10개 이상 파일 수정 전, 점수가 오르기만 하거나 스스로 100/완료면
  선제 적용. grep, 기계적 수정, 명확한 버그수정은 건너뛴다.
---

# Orchestrator Consultant Gate — 한국어

이 세션에서 **계획**을 쓴다(Grok, Codex, Claude, GPT, …). 부모를 바꾸지 않는다.

그 계획을 **GATE**로 보낸다. **다른 모델**이 읽기 전용으로 검수한다(파일·도구 없음). 의견이 돌아온다. 검수자는 실행자를 대체하지 않는다.

## 게이트

**필수** — 점수 보고 전, 10개 이상 파일 수정 전, 머지/배포 전.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성", diff 밖 증거 없음, 같은 에이전트가 작성·채점.

**하지 않음:** `grep` / 파일 읽기, 기계적 수정, 명확한 버그 수정. 매 턴 금지. ≤500단어.

물건은 **계획서**다. 코드 리뷰가 아니고, 두 번째 실행자도 아니다.

## 검수

세션 유지. 자식만 다른 모델:

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
python3 scripts/resolve-consult.py --name gpt --json
python3 scripts/resolve-consult.py --name gemini --json
```

기본 계열: `agent-model-registry get fable` → `claude-fable-5` (CLI 없으면 스크립트가 그 계열을 찍음). `--json` → `{host, registry, slug, name}`. `CONSULT_HOST`: cursor|claude|codex. Cursor만 Task slug. Claude/Codex에서 `cursor --list-models` 금지.

자식이 **막히면**(데이터 보관 정책, HTTP 402): `--name grok` 한 번, 또는 건너뛰고 다음 게이트. 멈추지 말 것.

`templates/fable-briefing.md`에 계획을 넣는다(증거 ≠ 해석). 반박 + 닫힌 3–5 + 열린 1: "내가 놓친 카테고리는?" 비밀 금지. `페이블 자문` / `fable 자문`은 트리거.

Cursor: `Task({ description: "Consult", subagent_type: "generalPurpose", model: "<slug>", prompt: <브리핑> })`. Claude Code: `Agent({ model: "<slug>", ... })`. Codex: `-m <slug>`. 도구 호출 지시 → reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

`templates/digest.md`. 완료: 모든 항목 accept / reject / defer + 이유, `min(코드 점수, 도달 가능 상한)`, 사용자에게 `host` + `registry` + `slug`. 상한은 외부 조건.
