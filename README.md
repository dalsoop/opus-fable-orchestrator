# orchestrator-consultant-gate-ko

머지·배포·큰 변경 전에, 지금 돌리는 에이전트는 그대로 두고 읽기 전용 전문가 의견을 받는 스킬입니다.

한국어판 (`ko`). 영어: 브랜치 [`main`](https://github.com/dalsoop/orchestrator-consultant-gate/tree/main).

```bash
npx skills add dalsoop/orchestrator-consultant-gate@ko -g -y
python3 scripts/resolve-consult.py --json
python3 eval/run.py
EVAL_LIVE=1 python3 eval/run.py
```

영어: `npx skills add dalsoop/orchestrator-consultant-gate -g -y`

<p align="center">
  <img src="assets/how-the-gate-works-ko.png" alt="실행 모델, 게이트, 자문 모델" width="920">
</p>

**실행 모델**(이 세션) → **게이트**(점수 전 / 10파일 전 / 머지 전) → **자문 모델**(읽기 전용).

자문 자식은 실행 모델과 다른 모델이다. 기본 계열은 `fable` → `claude-fable-5`. 이번 턴에 바꾸려면 `--name grok`, `--name gpt`, `--name gemini`.

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

`host-skills` 카탈로그 밖. 선택: `agent-model-registry set fable <id>`.
