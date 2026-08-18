# orchestrator-consultant-gate-ko

업무 지시 뒤, 전수조사해서 바꾸기 전에, 지금 돌리는 에이전트는 그대로 두고 계획에 대한 읽기 전용 전문가 의견을 받는 스킬입니다.

한국어판 (`ko`). 영어: 브랜치 [`main`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/main).

```bash
npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py
```

`npx`는 **파일**만 복사한다. 두 번째 의견은 **호스트**가 자식을 spawn 해야 한다. 설치만으로 E2E가 아니다.

영어: `npx skills add dalsoop/orchestrator-consultant-gate -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-ko.png" alt="한 AI가 계획을 세운다. 다른 AI가 검수한다." width="920">
</p>

한 AI가 업무 지시로 **계획**을 세운다. **GATE**는 전수조사해서 바꾸기 전. 다른 AI가 읽기 전용으로 **검수**하고 의견을 돌려준다. 세션은 그대로.

자문 자식은 실행 모델과 다른 모델이다. 기본 계열은 `fable` → `claude-fable-5`. 이번 턴에 바꾸려면 `--name grok`, `--name gpt`, `--name gemini`. 막히면 같은 `--json`의 `fallback_slug`.

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

`host-skills` 카탈로그 밖. 선택: `agent-model-registry set fable <id>`.
