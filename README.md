# Subject 9 Machine Vision

OpenCV 기반 제조 머신비전 검사기술을 단계적으로 학습하는 프로젝트입니다.
검사 대상: 병뚜껑 유무 (cap_on / cap_off)

## 실행 방법

```bash
source .venv/bin/activate       # 가상환경 켜기
python src/00_check_env.py      # 환경 확인 → Environment OK
python src/XX_파일이름.py        # 일차별 실습 코드 실행 (프로젝트 최상위에서)
```

## 폴더 구조

| 폴더         | 내용                         | Git |
|------------|----------------------------|-----|
| `src/`     | 실습 코드 (00~61)              | O   |
| `configs/` | Freeze한 판정 Rule (JSON)     | O   |
| `reports/` | 일차별 실험 · 판단 기록             | O   |
| `samples/` | 입력 이미지 · 영상                | X   |
| `outputs/` | 코드 실행 결과 이미지               | X   |
| `artifacts/` | 다시 만들 수 있는 생성 데이터 (정상 기준 .npz) | X   |

---

## Day 01 — 머신비전 검사문제 설계와 ROI

- 배운 것: 이미지 읽기 · ROI · 여러 이미지 / 영상 Frame / 스마트폰 실시간 영상에 ROI 적용
- 코드: `00_check_env.py` ~ `08_phone_camera_roi.py`
- 결과: 스마트폰 실시간 영상에서 cap_on / cap_off ROI 저장
- 핵심: 검사기를 바로 만드는 게 아니라, **어디를 보고 무엇으로 정상·불량을 구분할지** 먼저 정한다
- Mini Challenge: 주황 뚜껑 약병 5장 · 1차 ROI(바짝)에서 좌우 잘림 → 여유를 둔 최종 ROI로 5장 모두 포함 (판단: ROI를 조금 넓혀야 함)
- 자세한 기록: [problem_definition](reports/day01_problem_definition.md)

## Day 02 — Image Enhancement와 검사 영상 품질 개선

- 배운 것: 색 공간 · Brightness/Contrast · Gamma · CLAHE · Filter · Sharpening · Threshold/Otsu
- 코드: `09_color_space.py` ~ `17_day02_challenge.py`
- Challenge: 흰 뚜껑과 밝은 벽 분리 → 13가지 비교 후 `(B-R)/(B+G+R)` + Median 7 선택 (뚜껑 100% · 벽 0% · 고리와 분리)
- 핵심: 사람 눈에 선명한 것보다 **Otsu에서 안정적으로 분리되는 것**이 기준. 근본 해결은 촬영환경 개선
- 결과 이미지: `outputs/day02/compare/preprocess_compare.png` · `outputs/day02/challenge/`
- 자세한 기록: [parameter_table](reports/day02_parameter_table.csv) · [preprocess_reason](reports/day02_preprocess_reason.md)

## Day 03 — Morphology · Contour와 규칙 기반 판정

- 배운 것: Opening/Closing · Kernel 3·5·9 비교 · Contour · Area/Area Ratio/Count/BBox/Center
- 코드: `18_morphology_compare.py` ~ `23_day03_challenge.py`
- 병뚜껑 Rule: cap_on 0.661 / cap_off 0.459 → 중간값을 기준으로 OK/NG.
  640×480 재촬영 6장(Reference 2 · Test 4)에서 기준 0.3608 고정 → 4장 모두 일치 (소규모 확인)
- Challenge: 주황 뚜껑 약병 · HSV 주황 Mask → 가장 큰 덩어리 Area Ratio (ok 0.494 / ng 0.002)
  → 기준 0.2479 고정 후 새 사진 2장 모두 일치
- 추가: 원본 → Mask → Contour 3단계 비교 이미지를 직접 만들어 판정 근거를 시각화
- 핵심: 숫자를 먼저 정하지 않고, 측정한 뒤 기준을 만든다. 기준은 촬영 조건과 한 세트
- 자세한 기록: [reference_features](reports/day03_reference_features.csv) · [inspection_results](reports/day03_inspection_results.csv) · [rule_analysis](reports/day03_rule_analysis.md)

## Day 04 — Template · Feature Matching (광천김 로고)

- 배운 것: GrabCut · MeanShift(독립 실습), Template Matching, ORB · SIFT, RANSAC + Homography
- 코드: `24_day04_prepare.py` ~ `32_day04_challenge.py`
- 비교: 정면 사진 1장을 코드로 normal · shift · rot15 · scale90 4장으로 바꿔 같은 Reference로 측정
- 결과: Template은 normal 0.9997이지만 shift(로고가 화면 밖) · rot15에서 실패 / SIFT + Homography는 4장 모두 FOUND (Inlier Ratio 0.97~0.99)
- Mini Challenge: 실제 재촬영 4장에 SIFT + Homography 선택 → 4장 모두 FOUND, 반사가 있는 tilt_glare만 Ratio 0.721로 가장 낮음
- 핵심: 변화 종류(위치 · 회전 · 크기 · 반사)를 보고 방법을 고른다. 오늘은 측정까지, 판정 기준은 Day05 Calibration에서
- 자세한 기록: [reports/day04_rotation_compare.csv](reports/day04_rotation_compare.csv) · [reports/day04_method_selection.md](reports/day04_method_selection.md)

## Day 05 — Calibration · Rule Freeze · Test

### 목표
정상/불량 데이터로 OK·NG 기준을 정하고(Calibration), 기준을 JSON으로 고정한 뒤(Freeze), 처음 보는 데이터로 성능을 확인(Test)한다.

### 실습 (광천김 로고 · 33~38)
| 단계 | 파일 | 결과 |
|---|---|---|
| 공통 측정 모듈 | `src/day05_logo_features.py` | Template · SIFT · Homography 측정 함수 |
| Calibration | `34` · `35` | 12장 측정 → 225개 조합 탐색 |
| Rule Freeze | `36` → `configs/day05_logo_rules.json` | SIFT ≥ 129 AND Ratio ≥ 0.8664 (v1.0) |
| Test · 평가 | `37` · `38` | Acc 0.5 · Precision 0.5 · Recall 1.0 (FP 3 · FN 0) |

### Mini Challenge (드림카카오 72% 라벨 · 39)
- 직접 촬영: Reference 1 · Calibration 6(OK 3 · NG 3) · Test 4(OK 2 · NG 2)
- Rule `day05-mini-v1.0`: SIFT ≥ 44 AND Inlier Ratio ≥ 0.6657
- Test: TP 1 · TN 2 · FP 0 · **FN 1** → Accuracy 0.75 · Precision 1.0 · **Recall 0.5**
- FN 원인: 가운데 "72"만 가린 불량은 나머지 특징점이 그대로 맞아 통과. Calibration NG에 이 유형이 없었음
- 기록: `reports/day05_mini_challenge.md`

### 배운 점
- Test를 보고 기준을 바꾸면 Test가 아니다 → Rule은 Freeze 후 버전으로 관리
- Accuracy보다 **오류 종류(FN)**를 먼저 본다
- Rule은 Calibration에서 본 불량 유형까지만 막는다 → 다음 버전은 72 영역 ROI 검사

## Day 06 — OCR 기반 제조 문자 검사 (SN · Ch.-B.)

### 목표
제품에 인쇄된 문자를 OCR로 읽고, 형식(Regex)과 기대값(Expected SN)으로 검사해 OK / NG로 판정한다.

### 실습 (13자리 SN · 40~48)
| 단계 | 파일 | 결과 |
|---|---|---|
| 환경 확인 | `40` | Tesseract 5.5.0 · eng / kor / osd |
| ROI · 공통 모듈 | `41` · `day06_ocr_utils.py` · `day06_ocr_validation.py` | 6장 SN ROI · OCR / 문자열 검사 함수 |
| 전처리 비교 | `42` · `43` | original · gray 성공 / clahe · otsu · clahe_otsu 실패 |
| Rule Freeze | `44` → `configs/day06_ocr_rules.json` | original · PSM 7 · 숫자 Whitelist · `^[0-9]{13}$` (v1.0) |
| Batch · 평가 | `45` · `46` | OCR 6/6 · Inspection 6/6 · Expected Match 4/6 (교육용 NG 2장) |
| 환경 변화 | `47` · `48` | Low Contrast만 성공 · Blur(빈 값) · Tilt(빈 값) · Tilt+Deskew(714) · Glare(29) 실패 |

### Mini Challenge (Ch.-B. 코드 · 49)
- 새 사진 4장 · Whitelist A~Z·0~9·- · Regex `^[A-Z0-9-]+$`
- 결과: 3 / 4 성공 · 실패 1장 `TI776224-2D` → `TI776224-20` (D→0, Format은 통과)
- gray 재시도: 결과 동일 (TI776224-20) → 전처리만으로는 D/0 혼동이 해결되지 않음
- 기록: `reports/day06_mini_challenge.md`

### 배운 점
- OCR이 정확히 읽는 것 ≠ 제품이 정상인 것 → OCR Accuracy와 Inspection Accuracy를 따로 본다
- 사람 눈에 선명한 전처리가 OCR에 좋은 것은 아니다 → 실제 OCR 결과로 고른다
- Regex는 형식만 본다 → 비슷한 문자로 바꿔 읽은 오류는 기대값 비교에서 잡힌다
- 같은 Rule도 흐림 · 기울기 · 반사에서 실패한다 → 촬영환경 개선이 먼저
- 자세한 기록: [failure_analysis](reports/day06_failure_analysis.md) · [ocr_metrics](reports/day06_ocr_metrics.md)

## Day 07 — Anomaly Detection (MVTec AD bottle)

### 목표

정상 이미지만으로 정상 기준을 만들고, 처음 보는 병이 그 기준에서 얼마나 벗어났는지(Anomaly Score)로 Normal / Anomaly를 판정한다.

### 실습 (MVTec bottle · 50~60)

| 단계 | 파일 | 결과 |
|---|---|---|
| 환경 · 데이터 | `50` · `51` | PyTorch 확인 · 정상 209장 → Train 167 / Validation 42, Test 83 (정상 20 · 이상 63) |
| 공통 모듈 | `src/day07_anomaly_core.py` | 사전학습 ResNet18 layer3 Feature 추출 · 거리 계산 · Heatmap |
| 정상 기준 | `52` | Train 167장 Feature 평균 → Vector (256,) · Map (256, 14, 14) |
| Threshold | `53` · `54` | 정상 Validation Score로 90 / 95 / 99 Percentile 비교 |
| Rule Freeze | `55` → `configs/day07_anomaly_rules.json` | 95 Percentile · Threshold 0.067458 (v1.0) |
| Test · 평가 | `56` · `57` | TP 59 · TN 18 · FP 2 · FN 4 → Acc 0.9277 · Precision 0.9672 · Recall 0.9365 |
| Heatmap | `58` | 대표 8장 Heatmap · Overlay와 Ground Truth Mask 비교 |
| Challenge | `59` · `60` | 정상 1장 5조건 변형 → Dark · Bright · Shift FP / Blur · Rotation PASS |

- 종류별: broken_large 20/20 · contamination 21/21 · broken_small 18/22 (FN 4) · good 18/20 (FP 2)

### Mini Challenge (61)

- 다른 정상 이미지(`001.png`)에 강도를 직접 정해 같은 Rule로 검사
- Dark (alpha 0.75) 0.089038 **FP** · Blur (7) 0.050097 PASS · Rotation (10°) 0.046322 PASS
- 덜 어둡게 해도 FP → 밝기 변화에 매우 민감
- 기록: `reports/day07_mini_challenge.md`

### 배운 점

- 딥러닝(ResNet18)은 특징만 뽑고, 판정은 거리 + Threshold 규칙이 한다 → 모델은 학습하지 않았다
- 작은 파손은 196칸 평균 Vector에서 차이가 희석되어 FN이 된다 → Threshold 조정만으로는 해결이 어렵다
- 검사기는 '결함'이 아니라 '정상 사진과 다름'을 잰다 → 밝기·위치만 바뀌어도 정상이 FP가 된다
- Test·Challenge 결과를 보고 Threshold를 바꾸지 않는다 → 개선은 Validation으로 다시 정해 v1.1로
- 자세한 기록: [test_metrics](reports/day07_test_metrics.md) · [failure_analysis](reports/day07_failure_analysis.md) · [challenge_results](reports/day07_challenge_results.csv)