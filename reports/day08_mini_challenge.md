# Day08 Mini Challenge

## 1. Support Count 비교

| Support | Accuracy | FP | FN |
|---:|---:|---:|---:|
| 1 | 0.70 | 1 | 5 |
| 3 | 0.80 | 0 | 4 |
| 5 | 0.90 | 0 | 2 |

가장 달라진 점:
Support가 늘수록 FN이 크게 줄었다(5 → 4 → 2). 불량 1장으로는 다양한 작은 파손 모양을 대표하지 못했다.
normal/006은 1장일 때만 FP(One-shot과 같은 오탐), broken_small/000·007은 1·3·5장 모두 FN.
Support는 이름순 앞 k장으로 골랐으므로, 다른 조합이면 결과가 달라질 수 있다.

---

## 2. contamination Synthetic Defect

생성 수: 5장 (scale 0.6~1.0, rotation -10~10°, seed 42)

가장 자연스러웠던 이미지: synthetic_004.png

가장 어색했던 이미지: synthetic_003.png

한 줄 이유:
004는 어둡고 작은 결함이 병 입구 안에 녹아들어 경계가 거의 안 보였지만,
003은 큰 갈색 원판이 테두리를 넘어 바깥 링까지 덮고 원형 경계가 뚜렷해 붙여 넣은 티가 났다.
5장 중 4장이 같은 Patch(갈색 원판)라 모양이 단조롭고, scale을 줄여도 원본 오염이 커서 여전히 크게 보였다.
→ 개선: 경계 Blending, 붙일 위치를 입구 안쪽으로 제한, 더 작은 scale, Defect Source 다양화

---

## 3. 상황별 방법 선택

정상 데이터 충분 / 불량 0장:
→ Anomaly Detection (정상만으로 기준 생성, 7일차 Acc 0.9277). Zero-shot은 다음 검토 후보

Normal Reference 1장 중심:
→ One-shot (Reference 1장 + 정상 Calibration으로 Threshold, Acc 0.85)

Normal / Anomaly 소수 예제:
→ Few-shot (Prototype 비교로 FP 1 → 0, Acc 0.90)

불량 데이터 자체가 부족함:
→ Defect Generation + 추가 수집 (합성 20장 중 Keep 후보 3장 — 품질 확인 필수)

---

## 오늘의 한 줄 결론

데이터가 적을 때 검사 방법을 선택할 때 가장 중요하다고 생각한 점:
가진 데이터의 양과 종류에 맞는 방법을 고르고, 같은 Query로 비교해야 한다.
어떤 방법도 broken_small/007은 잡지 못했다 — 방법보다 특징의 한계가 남아 있다.