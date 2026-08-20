---
name: orchestrator-consultant-gate-ko
version: 1.19.0
kind: skill
license: MIT
compatibility: 읽기 전용 하위 에이전트를 띄울 수 있는 호스트(Cursor Task, Claude Code Agent, Codex, Grok TUI, …).
metadata:
  author: dalsoop
  version: "1.19.0"
  locale: ko
description: >-
  업무 지시 뒤, 전수조사해서 바꾸기 전에 계획을 읽기 전용으로 검수받는다. 지금
  세션 에이전트는 바꾸지 않는다. 검수자는 페이블. 오케스트레이션에 착수하기 전에
  실행 문서를 비판한다. 페이블 검수받아봐, 페이블로 검수해봐, 페이블 검수,
  페이블로 검수, opus 4.6, opus 4.6 검수, 컨설턴트 게이트, 전문가 의견,
  자문 받아와, fable 자문, 페이블 자문, 전수조사, 업무 지시일 때 쓴다. 전수조사 후 수정에
  착수하기 전, 그 계획으로 파일 10개 이상을 고치기 전에 선제 적용. grep,
  기계적 수정, 명확한 버그수정은 건너뛴다. 토큰을 추가로 쓴다. 자문은 정답이 아니다.
  효과는 자식에게 넘기기 전, 계획과 자식 프롬프트에서 난다. 머지 때가 아니다.
  사용자가 영어면 orchestrator-consultant-gate(브랜치 main)를 쓰고 이 사본을
  실행하지 않는다.
---

# Orchestrator Consultant Gate — 한국어

이 세션에서 **실행 문서**를 작성한다(Grok, Codex, Claude, GPT, …). 부모를 바꾸지 않는다.

실행 문서는 계획과, 오케스트레이션에 넘길 자식 프롬프트다. **오케스트레이션에 착수하기 전**에 비판적으로 다듬는다. **기본 검수자는 페이블**이다. 읽기 전용으로 띄운다(파일·도구 없음). 반박한다. 소화는 네가 한다. 나온 말은 **정답이 아니다.** 항목마다 accept / reject / defer 와 이유를 붙인다.

## 게이트

**필수** — **업무 지시** 뒤, **오케스트레이션에 착수하기 전**. 계획한 **전수조사해서 바꾸기**에 들어가기 전이다. 머지·배포 때가 아니다. 사용자가 페이블 검수받아봐, 페이블로 검수해봐, 페이블 검수, 페이블로 검수라고 해도 같다.

**언어.** 이 사본은 한국어다. 사용자가 영어면 **이 사본을 실행하지 않는다.** `orchestrator-consultant-gate`(브랜치 `main`)를 읽고 따른다. 없으면 `npx skills add dalsoop/orchestrator-consultant-gate -g -y`. 이 스킬을 영어로 번역해서 계속하지 않는다.

**필수** — 성능 개선 계획(놓친 병목을 하나 더 찾는다), 자식 프롬프트가 있는 오케스트레이션(프롬프트가 하나라도 어긋나면 배치가 망가진다. 빈칸을 채운다), 누락될 수 있는 실행 문서.

**필수** — 다음 중 2개 이상: 점수가 오르기만 함, 스스로 100 / "완료" / "달성", diff 밖 증거 없음, 같은 에이전트가 작성·채점.

**하지 않음:** `grep` / 파일 읽기, 기계적 수정, 명확한 버그 수정. 매 턴 금지. 토큰 비용이 이득보다 크면 건너뛴다. ≤500단어.

물건은 **실행 문서**다. 코드 리뷰가 아니고, 두 번째 실행자도 아니다.

## 효과

이득은 **자식에게 넘기기 전**에, 소화한 뒤 고친 실행 문서에서 난다. 놓친 병목을 하나 더 적거나, 자식 프롬프트의 빈칸을 채우거나, 빠진 분류를 계획에 넣는 식으로 보인다. 점수가 오르거나, 머지 게이트가 열리거나, 다른 에이전트가 일을 대신하는 식으로는 보이지 않는다.

자식 spawn에 토큰이 든다. 돌아온 말은 확률적이다. 항목을 전부 받아들이면 토큰을 쓰고 거짓 확신만 남는다. 계획이 grep이거나, 오타이거나, 버그 한 건이면 건너뛴다.

spawn이 막히면 폴백을 한 번 하거나 건너뛴다. 건너뛴 게이트에는 효과가 없다. 자식을 이미 보낸 뒤에 돌린 게이트에도 효과가 없다.

## 검수

세션 유지. 기본 자식은 페이블(`agent-model-registry get fable`). spawn은 `--json`의 `slug`. 다른 모델은 이번 턴 덮어쓰기만:

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
python3 scripts/resolve-consult.py --name gpt --json
python3 scripts/resolve-consult.py --name gemini --json
python3 scripts/resolve-consult.py --name opus --json
```

`--json` → `{host, registry, slug, name, fallbacks, fallback_slug, spawn, read_only}`. `fallbacks`에 grok와 opus 4.6이 있다. `CONSULT_HOST`: cursor|claude|codex|grok. `slug`를 쓴다. 스킬에 모델 id를 복사하지 않는다. Cursor만 Task slug(`thinking-high`가 목록에 있으면). `--name opus`는 레지스트리 opus **4.6**, 호스트가 받으면 `[1m]`(`generation_ok`). Claude/Codex/Grok에서 `cursor --list-models` 금지. CLI 없으면 스크립트가 그 계열을 찍음. Grok TUI는 `GROK_AGENT=1`.

자식이 **막히면**(Cursor Review Data Policy, HTTP 402, Grok가 페이블을 못 띄움): `--name grok` 또는 `--name opus` 한 번. opus는 4.6이어야 한다. 아니면 건너뛰고 다음 게이트. 멈추지 말 것. Grok에서는 Claude CLI가 있으면 `claude -p --model <slug> --max-turns 1`.

`templates/` 는 뼈대다. **부모 에이전트**가 채운다. 사람이 게이트 전에 쓰지 않는다.

`templates/fable-briefing.md`에 실행 문서를 넣는다(증거 ≠ 해석). 자식에게: 이 계획의 검수자이지 두 번째 실행자가 아니다. 동의하지 마라. 계획을 다시 짜지 마라. 반박 + 닫힌 3–5 + 열린 1: "내가 놓친 카테고리는?" 비밀 금지. `페이블 검수받아봐` / `페이블로 검수해봐` / `페이블 검수` / `페이블 자문` / `fable 자문`은 트리거.

Cursor: `Task({ description: "Consult", subagent_type: "generalPurpose", model: "<slug>", prompt: <브리핑> })`. Task가 막히면 `--name grok` 또는 `--name opus`(opus 4.6). Claude Code: `Agent({ model: "<slug>", ... })`. Codex: `-m <slug>`. Grok: Claude CLI가 있으면 `claude -p --model <slug> --max-turns 1`. slug가 Grok 모델이면 `spawn_subagent`. 도구 호출 지시 → reject. Timeout → 진행, 다음 게이트에서 재시도.

## 소화

자문이 오면 **부모 에이전트**가 `templates/digest.md`를 채운다. 완료: 모든 항목 accept / reject / defer + 이유, `min(코드 점수, 도달 가능 상한)`, 사용자에게 `host` + `registry` + `slug` + `spawn_ok` + `read_only` + `fallback_used`. 상한은 외부 조건. 파일 점수와 라이브 spawn 점수를 더하지 말 것. 반박이 없는 자문은 완료가 아니다. 자문은 **정답이 아니다.**

```bash
python3 scripts/resolve-consult.py --record --ok --read-only
python3 scripts/resolve-consult.py --record --ok --read-only --fallback-used
```
