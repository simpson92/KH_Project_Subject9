# Day05 Mini Challenge

## 검사 대상
롯데 드림카카오 72% 원통형 용기의 노란 라벨
(DREAM CACAO 72% 사각형 영역)

## OK 기준
노란 라벨 전체가 가려지지 않고 보이며,
기준 라벨(reference_label.jpg)과 충분히 Matching됨

## NG 기준
카드로 노란 라벨의 일부가 가려져
기준 라벨과 정상적인 Matching이 어려움

## Calibration 데이터
- OK: 3장 (ok_01~03 · 위치 · 거리 · 각도를 조금씩 바꿈)
- NG: 3장 (ng_01 왼쪽 아래 · ng_02 위쪽 · ng_03 오른쪽 아래를 가림)

## Test 데이터
- OK: 2장 · NG: 2장 (test_ng_01 오른쪽 절반 · test_ng_02 72 전체를 가림)
- Rule을 고정하기 전까지 Test 이미지는 측정하지 않음

## 확인한 Feature
- Template · SIFT Good · Inlier · Inlier Ratio 4개 측정
- 평균은 모두 OK > NG지만, 범위는 모두 겹침
- 겹침 원인: ok_03(멀리 · 위에서 찍어 값이 낮음) / ng_01 · ng_03(모서리만 가려 글자가 많이 남음)
- Template은 ok_01만 높고 나머지는 NG와 섞여 제외

## Calibration 결과

### OK
- ok_01: SIFT 164 · Ratio 0.7866 (Reference와 거의 같은 위치라 가장 쉬운 OK)
- ok_02: SIFT 119 · Ratio 0.6555
- ok_03: SIFT 101 · Ratio 0.5644 (멀리 · 위에서 찍어 가장 낮음)

### NG
- ng_01 (왼쪽 아래 가림): SIFT 114 · Ratio 0.6404
- ng_02 (위쪽 가림): SIFT 44 · Ratio 0.3636
- ng_03 (오른쪽 아래 가림): SIFT 124 · Ratio 0.6532

## 선택한 Rule
Homography Found = 1
AND SIFT Good Match >= 44
AND Inlier Ratio >= 0.6657
(day05-mini-v1.0 · configs/day05_mini_rules.json)

- 선택 방법: 35번 방식으로 SIFT+Ratio · SIFT+Inlier 각 225개 조합 시험 → 둘 다 FN 0 · FP 2로 같아 광천김과 같은 SIFT+Ratio 선택
- Calibration 성적: Accuracy 0.6667 · TP 3 · TN 1 · FP 2 · FN 0
- 주의: SIFT 44는 최솟값이라 사실상 Ratio 하나로 판정. ok_02(0.6555)와 ng_03(0.6532)의 차이가 0.0023뿐이라 기준을 그 틈에 맞추지 않음

## Test 결과
| file | actual | predicted | SIFT | Ratio | NG Reason |
|---|---|---|---|---|---|
| test_ok_01 | OK | OK | 132 | 0.7652 | - |
| test_ok_02 | OK | OK | 129 | 0.7132 | - |
| test_ng_01 (오른쪽 절반 가림) | NG | NG | 67 | 0.4328 | LOW_INLIER_RATIO |
| test_ng_02 (72 가림) | NG | **OK** | 83 | 0.6867 | - |

- TP 1 · TN 2 · FP 0 · **FN 1**
- Accuracy 0.75 · Precision 1.0 · **Recall 0.5**

## 가장 눈에 띄는 결과
- test_ng_02(72 가림)가 모든 조건을 통과해 **FN** 발생 → NG Reason이 없어서 Failure Cause로 분석
- Failure Cause 1: 72는 라벨의 일부라 가려도 나머지 글자 · 모서리 특징점의 위치가 맞아 Ratio 0.6867 유지
- Failure Cause 2: Calibration NG 3장은 모두 가장자리 가림이라 "가운데 가림" 유형이 없었음
- Accuracy는 Calibration(0.6667)보다 올랐지만 오류가 FP → FN으로 바뀌어 더 위험한 결과
- Test를 보고 기준을 바꾸지 않음 (v1.0 유지)

## 다음 버전 아이디어 (v1.1)
- Calibration NG에 가운데 72 가림 사진 추가
- Homography로 찾은 라벨 안에서 72 영역만 ROI로 잘라 따로 검사

## 한 줄 정리
SIFT + Homography는 "라벨이 제자리에 있는가"는 잘 보지만, 일부 글자가 사라진 불량은 놓친다. Rule은 Calibration에서 본 불량 유형까지만 막는다.