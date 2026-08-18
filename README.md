# orchestrator-consultant-gate-ko

오케스트레이션하는 에이전트를 위한 컨설턴트 게이트. 세션 모델은 유지. 점수·머지 게이트에서 읽기 전용 자식.

한국어판 (`ko`). 영어: 브랜치 [`main`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/main).

```bash
npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py
```

영어: `npx skills add dalsoop/orchestrator-consultant-gate -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-ko.png" alt="오케스트레이터 컨설턴트 게이트" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

`host-skills` 카탈로그 밖. 선택: `agent-model-registry set fable <id>`.
