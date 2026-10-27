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

| 폴더 | 내용 | Git |
|---|---|---|
| `src/` | 실습 코드 (00~23) | O |
| `reports/` | 일차별 실험 · 판단 기록 | O |
| `samples/` | 입력 이미지 · 영상 | X |
| `outputs/` | 코드 실행 결과 이미지 | X |

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