# orchestrator-consultant-gate-ko

클로드코드가 더 틀리고 말이 어려워지면 **세팅**이다(`--install-claude`: opus 4.6 핀 + 비유). 글자 수가 지표가 아니다. CLAUDE.md에 be concise를 붙이지 않는다. 오케스트레이션에 착수하기 전에, 실행 문서(계획과 자식 프롬프트)를 읽기 전용으로 비판하는 스킬입니다. 지금 세션의 에이전트는 바꾸지 않습니다. 검수는 토큰을 추가로 쓰고, 나온 말은 확률적이므로 정답이 아닙니다.

한국어판 (`ko`). 영어: 브랜치 [`main`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/main).

```bash
npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y
python3 scripts/resolve-consult.py --install-claude --json
python3 scripts/resolve-consult.py --list --json
python3 scripts/resolve-consult.py --exec-spawn --briefing templates/fable-briefing.md
python3 scripts/resolve-consult.py --print-spawn
python3 scripts/resolve-consult.py --report --json
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py   # Cursor/Claude spawn. Grok는 claude -p --max-turns 1.
```

`npx`는 **파일**만 복사한다. 두 번째 의견은 **호스트**가 자식을 spawn 해야 한다. 설치만으로 E2E가 아니다.

영어: `npx skills add dalsoop/orchestrator-consultant-gate -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-ko.png" alt="한 AI가 계획을 세운다. 다른 AI가 검수한다." width="920">
</p>

한 AI가 업무 지시로 **실행 문서**를 쓴다. **GATE**는 오케스트레이션과 전수조사해서 바꾸기 전이다. 페이블이 읽기 전용으로 **반박**한다. 놓친 병목을 하나 더 찾고, 자식 프롬프트의 빈칸을 채우며, 누락을 잡는다. 효과는 **자식에게 넘기기 전** 그 문서에서 난다. 머지 때가 아니다. 의견이 돌아오면 소화한다. 세션은 그대로다. 자문은 정답이 아니다.

클로드코드 실수와 어려운 말: `--install-claude`(opus 4.6 + 비유, `keep-coding-instructions`). `--install-hook`은 PreToolUse. 검수자는 `--list`에서 고른다. 기본은 페이블(`agent-model-registry get fable`). spawn은 `--json`의 `slug`. 페이블이 막히면 목록의 opus 4.6이지 grok가 아니다. `--report`는 사용 이력이지 검수 품질이 아니다. Grok는 `--list` 다음 `--print-spawn`만 실행한다. 손으로 `claude -p`를 만들지 않는다. 기본 eval은 정적이다. `EVAL_LIVE=1`은 요청했을 때만. 호스트: Cursor, Claude Code, Codex, Grok TUI(`GROK_AGENT=1`). 세션 에이전트가 게이트에서 `templates/`를 채운다.

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

host-skills-mono에 `orchestrator-consultant-gate-ko`로 들어 있다(배포: personal-mac). 공개 설치는 여전히 `npx skills add`. 선택: `agent-model-registry set fable <id>`.
