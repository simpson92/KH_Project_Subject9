# Day04 Mini Challenge

## 검사 이미지
samples/day04/challenge/ 의 실제 재촬영 사진 4장
- shift.jpg (1346×584) · rotate.jpg (861×417)
- distance.jpg (387×157) · tilt_glare.jpg (1656×777)

## 주요 변화
- 4장 모두 포장지 전체가 아닌 로고 근접 사진 → Template(440×198)과 로고 크기가 크게 다름
- rotate: 회전 · tilt_glare: 기울기 + 비닐 반사
- distance: 이미지가 Template보다 작음

## 선택한 방법
SIFT + Homography (SIFT_HOMOGRAPHY)

## 선택 이유
- distance.jpg가 Template보다 작아 Template Matching은 실행할 수 없음
- 크기 · 회전 변화가 크므로 SIFT 특징점이 유리함
- Homography로 로고 위치를 사각형으로 확인할 수 있고, Good Match · Inlier · Inlier Ratio를 함께 기록할 수 있음

## 예상되는 한계
- tilt_glare는 반사로 특징점이 줄어 Inlier Ratio가 낮아질 수 있음
- 로고가 크게 가려지거나 많이 흐리면 NOT_FOUND가 될 수 있음

## 결과
| 이미지 | 크기 | Good Match | Inlier | Inlier Ratio | Status |
|---|---|---|---|---|---|
| shift.jpg | 1346×584 | 347 | 305 | 0.879 | FOUND |
| rotate.jpg | 861×417 | 389 | 360 | 0.925 | FOUND |
| distance.jpg | 387×157 | 365 | 343 | 0.940 | FOUND |
| tilt_glare.jpg | 1656×777 | 294 | 212 | 0.721 | FOUND |

4장 모두 로고 위치를 사각형으로 찾았다. (outputs/day04/challenge/)

## 관찰
- rotate: 사각형이 로고 기울기를 따라 비스듬하게 그려짐 → 회전 대응 확인
- tilt_glare: 사각형이 사다리꼴로 그려져 원근 변화까지 따라감. 다만 글자 위 반사로 Inlier Ratio가 0.721로 가장 낮음
- distance: Template보다 작은 사진(387×157)이라 Template Matching은 실행할 수 없지만, SIFT + Homography는 Ratio 0.940으로 가장 안정적
- 사각형이 로고보다 크고 일부가 화면 밖으로 나가는 것은 Reference가 로고 주변 여백까지 포함한 영역이기 때문 (오류 아님)
- 코드 변형 실험(Inlier Ratio 0.97~0.99)보다 낮은 이유: 실제 재촬영에서 생기는 흔들림 · 반사 · 원근 편차

## 실제로 확인한 한계
- 반사가 있으면 특징점 연결이 줄어듦 (tilt_glare)
- 4장 모두 정상 로고 사진이라 "찾을 수 있다"만 확인함. 다른 로고 · 가려진 로고(NG)에서 값이 얼마나 떨어지는지는 확인하지 못함 → 5일차 Calibration에서 OK · NG를 함께 재야 기준을 만들 수 있음

## Threshold
Day05 Calibration 후 결정