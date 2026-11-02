# Day07 Mini Challenge

Source: samples/day07/test/normal/001.png
Rule: day07-anomaly-v1.0 (Threshold 0.067458, 변경 없음)

| 변형 | 내가 정한 값 | 예상 | 실제 Score | 결과 |
|---|---|---|---|---|
| Dark | alpha = 0.75 | 기록 없음 | 0.089038 | FP |
| Blur | kernel = 7 | 기록 없음 | 0.050097 | PASS |
| Rotation | angle = 10° | 기록 없음 | 0.046322 | PASS |

가장 Score가 높았던 조건:
Dark (0.089038) — Threshold보다 0.0216 높음

내 예상과 달랐던 조건:
실행 전 예상을 따로 기록하지 못함.
Challenge 결과를 기준으로 보면 Dark(덜 어둡게 해도 FP)와
Rotation(더 많이 돌려도 PASS, Score는 오히려 낮음)이 예상하기 어려운 결과였다.

한 줄 정리:
밝기는 25%만 줄여도 정상이 FP가 될 만큼 민감하고,
Blur(7)와 회전(10°)은 Threshold보다 한참 낮아 이 병 사진에서는 영향이 작았다.