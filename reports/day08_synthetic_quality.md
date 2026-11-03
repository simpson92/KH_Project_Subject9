# Day08 Synthetic Quality Check

## 확인 대상

outputs/day08/cutpaste/generated

## 검수 결과

| 파일 | Keep / Reject | 간단한 이유 |
|---|---|---|
| synthetic_000.png | Reject | 결함이 너무 크고 길게 퍼져 있음 |
| synthetic_004.png | Keep | 결함이 비교적 작고 제품 영역 안에 위치함 |
| synthetic_007.png | Reject | 결함 크기가 크고 Patch 경계가 눈에 띔 |
| synthetic_013.png | Keep | 결함이 국소적으로 나타나 비교적 자연스러움 |
| synthetic_017.png | Keep | 결함 크기가 작고 한 영역에 모여 있음 |

## 확인 결과

일부 이미지는 비교적 자연스럽게 생성되었지만,
일부 이미지는 결함이 너무 크거나 Patch 경계가 눈에 띄었다.

따라서 Synthetic 이미지는 생성 후 바로 사용하지 않고
품질을 확인하여 사용할 이미지만 선택해야 한다.