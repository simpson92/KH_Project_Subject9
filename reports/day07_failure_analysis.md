# Day07 Failure Analysis

Rule: day07-anomaly-v1.0 (Threshold 0.067458)
Test 결과: TP 59 · TN 18 · FP 2 · FN 4 → Accuracy 0.9277 · Precision 0.9672 · Recall 0.9365

## Test FP

File: samples/day07/test/normal/015.png

Score: 0.070634 (Threshold보다 0.003176 높음)

원인 추정:
FP 2장(006: 0.069446, 015: 0.070634)은 모두 Threshold를 아주 조금 넘었다.
결함이 아니라 정상 Score 분포의 꼬리에 있는 사진으로 보인다.
95 Percentile로 정했기 때문에 Validation에서도 정상 일부가 기준을 넘었고, Test에서도 같은 현상이 나타났다.

## Test FN

File: samples/day07/test/anomaly/broken_small/000.png

Score: 0.053315 (Threshold보다 0.014143 낮음 — FN 4장 중 가장 낮음)

원인 추정:
작은 파손은 14×14 = 196칸 중 몇 칸에만 걸린다.
판정은 196칸을 평균 낸 Feature Vector로 하므로 차이가 희석되어 Score가 낮게 나온다.
FN 4장 모두 broken_small이고 Score가 0.0533~0.0657로 정상과 비슷한 범위라,
Threshold를 내리면 정상 FP가 크게 늘어나 Threshold만으로는 해결이 어렵다.

## Challenge FP

변형 조건: Dark (alpha 0.60)

Score: 0.123438 (5가지 조건 중 가장 높음)

원인 추정:
제품은 정상이고 밝기만 바뀌었는데 Feature 전체가 달라졌다.
Bright(0.104316)와 Shift(0.076092)도 FP였다.
Mini Challenge에서 덜 어둡게(alpha 0.75) 해도 0.089038로 FP였다 → 밝기 변화에 매우 민감하다.
반면 Blur(0.065153)는 기준보다 0.002305 낮아 간신히 PASS였다.

## 한 줄 정리

현재 Baseline이 잘 동작한 경우:
큰 파손(broken_large 20/20), 오염(contamination 21/21), 약한 Blur·회전(Rotation 6°: 0.054645, Mini 10°: 0.046322)

현재 Baseline이 약했던 경우:
작은 파손 4장 미검출(FN), 밝기 변화(Dark·Bright)와 위치 이동(Shift)에 따른 정상 오탐(FP)

다음에 개선하고 싶은 점:
1. 촬영 조명 고정 또는 밝기 정규화
2. 평균 Feature Vector 대신 위치별 차이의 최댓값으로 판정하는 v1.1 검토
   (Validation으로 새 Threshold를 정하고 v1.1로 Freeze한 뒤 다시 Test)