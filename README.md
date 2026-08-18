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

### 옵션 모델

이미 세션이 있으면 그 모델을 유지. 고를 때만:

| 역할 | 모델 | 가성비 |
|---|---|---|
| 실행 | **Opus 4.6** (Opus 5.0 아님) | 작성·실행에 가성비. 이 스킬 때문에 부모를 5.0으로 올리지 말 것. |
| 자문 | **Fable 5** | 짧은 읽기 전용 의견에 가성비. 실행자로 쓰면 비싸다. |

<p align="center">
  <img src="assets/how-the-gate-works-ko.png" alt="세션 모델 유지, 옵션은 Opus 4.6 실행과 Fable 5 자문" width="920">
</p>

[`SKILL.md`](SKILL.md) · [`templates/`](templates/) · [`scripts/`](scripts/) · [`eval/`](eval/) · MIT

[![skills.sh](https://skills.sh/b/dalsoop/orchestrator-consultant-gate)](https://skills.sh/dalsoop/orchestrator-consultant-gate)

`host-skills` 카탈로그 밖. 선택: `agent-model-registry set fable <id>`.
