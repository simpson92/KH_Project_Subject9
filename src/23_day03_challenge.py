from pathlib import Path

import cv2
import numpy as np

input_dir = Path("samples/day03/challenge")
output_dir = Path("outputs/day03/challenge")
output_dir.mkdir(parents=True, exist_ok=True)

# 1일차 Mini Challenge에서 정한 최종 ROI (사진 크기 1265×1012 기준)
X1, Y1, X2, Y2 = 395, 120, 915, 330

# ------------------------------------------
# TODO 1 · 검사 문제에 맞는 전처리 — HSV 주황색 Mask
# OpenCV의 HSV 범위: H 0~179 · S 0~255 · V 0~255
# ------------------------------------------
LOWER_ORANGE = np.array([5, 120, 100])     # 주황의 아래 경계 (색상 · 채도 · 밝기)
UPPER_ORANGE = np.array([22, 255, 255])    # 주황의 위 경계


def make_orange_mask(image):
    roi = image[Y1:Y2, X1:X2]                       # 1일차 ROI만 잘라서 사용
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)      # BGR → HSV (색상과 밝기를 분리)
    mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)   # 범위 안 = 255(흰색), 밖 = 0
    return roi, mask


# ------------------------------------------
# TODO 2 · Morphology — 3일차 기준과 같은 3×3 타원, Opening → Closing 1회
# ------------------------------------------
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
MIN_CONTOUR_AREA_RATIO = 0.001        # ROI의 0.1% 미만 덩어리는 Noise로 제외 (20번 코드와 같음)


def clean_mask(mask):
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL, iterations=1)    # 작은 흰 점 제거
    return cv2.morphologyEx(opened, cv2.MORPH_CLOSE, KERNEL, iterations=1)   # 작은 구멍 메우기


# ------------------------------------------
# TODO 3 · Contour를 찾고 Feature 계산
# ------------------------------------------
def measure(cleaned):
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    roi_area = float(cleaned.shape[0] * cleaned.shape[1])
    valid = [c for c in contours if cv2.contourArea(c) >= roi_area * MIN_CONTOUR_AREA_RATIO]
    if not valid:                                   # 주황 덩어리가 하나도 없으면
        return 0.0, 0, None
    largest = max(valid, key=cv2.contourArea)       # 가장 큰 주황 덩어리
    return cv2.contourArea(largest) / roi_area, len(valid), largest


# Rule을 만들 두 장의 Feature를 먼저 측정 (교재 27절: 먼저 측정하고 그다음 Rule)
for name in ["ok_01", "ng_01"]:
    image = cv2.imread(str(input_dir / f"{name}.jpg"))
    if image is None:
        raise FileNotFoundError(input_dir / f"{name}.jpg")

    roi, mask = make_orange_mask(image)
    cleaned = clean_mask(mask)
    ratio, count, largest = measure(cleaned)

    result = roi.copy()
    if largest is not None:
        cv2.drawContours(result, [largest], -1, (0, 255, 0), 2)   # 가장 큰 덩어리를 초록 선으로
    cv2.imwrite(str(output_dir / f"{name}_mask.jpg"), mask)
    cv2.imwrite(str(output_dir / f"{name}_cleaned.jpg"), cleaned)
    cv2.imwrite(str(output_dir / f"{name}_contour.jpg"), result)

    print(f"{name}: largest_area_ratio = {ratio:.4f} · valid_count = {count}")

# ------------------------------------------
# TODO 4 · 측정값을 본 뒤 Rule 작성
# ok_01 = 0.4941, ng_01 = 0.0017 → 두 값의 중간을 기준으로 사용
# ------------------------------------------
THRESHOLD = 0.2479


def judge(ratio):
    if ratio >= THRESHOLD:              # 주황 덩어리가 ROI의 약 25% 이상 → 뚜껑 있음
        return "OK", ""
    return "NG", "NG_NO_ORANGE_CAP"     # 주황 덩어리가 작거나 없음 → 뚜껑 없음


for name in ["ok_01", "ng_01"]:
    image = cv2.imread(str(input_dir / f"{name}.jpg"))
    roi, mask = make_orange_mask(image)
    ratio, count, largest = measure(clean_mask(mask))
    decision, reason = judge(ratio)
    print(f"{name}: ratio = {ratio:.4f} → Decision: {decision} {reason}")


# ------------------------------------------
# 새 사진 확인 — Rule(THRESHOLD)은 고정한 채 그대로 적용 (교재 28절)
# ------------------------------------------
TEST_IMAGES = [("ok_02", "OK"), ("ng_02", "NG")]    # (파일 이름, 실제 정답)
correct = 0

for name, expected in TEST_IMAGES:
    image = cv2.imread(str(input_dir / f"{name}.jpg"))
    roi, mask = make_orange_mask(image)
    ratio, count, largest = measure(clean_mask(mask))
    decision, reason = judge(ratio)

    is_correct = decision == expected               # 판정이 정답과 같은가?
    correct += int(is_correct)

    result = roi.copy()
    if largest is not None:
        cv2.drawContours(result, [largest], -1, (0, 255, 0), 2)
    color = (0, 200, 0) if is_correct else (0, 0, 255)   # 맞으면 초록 글자, 틀리면 빨간 글자
    cv2.putText(result, f"{decision} {ratio:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imwrite(str(output_dir / f"{name}_result.jpg"), result)

    print(f"[Test] {name}: ratio = {ratio:.4f} → {decision} (정답 {expected}) {'맞음' if is_correct else '틀림'}")

print(f"확인 이미지 수: {len(TEST_IMAGES)} · 올바른 판정: {correct} · 틀린 판정: {len(TEST_IMAGES) - correct}")


# ------------------------------------------
# 비교 이미지 — 원본 ROI | 주황 Mask | Contour + 판정 을 한 줄로
# ------------------------------------------
def label(img, text):
    img = img.copy()
    cv2.rectangle(img, (0, 0), (img.shape[1], 34), (255, 255, 255), -1)   # 글자 배경 흰 띠
    cv2.putText(img, text, (8, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    return img


def make_row(name):
    image = cv2.imread(str(input_dir / f"{name}.jpg"))
    roi, mask = make_orange_mask(image)
    cleaned = clean_mask(mask)
    ratio, count, largest = measure(cleaned)
    decision, reason = judge(ratio)

    mask_bgr = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)   # 흑백(1채널)을 3채널로 바꿔야 옆에 붙일 수 있음
    contour = roi.copy()
    if largest is not None:
        cv2.drawContours(contour, [largest], -1, (0, 255, 0), 3)

    return cv2.hconcat([                                     # 같은 높이의 이미지 3장을 가로로 붙임
        label(roi, f"{name} | original ROI"),
        label(mask_bgr, "orange mask (HSV)"),
        label(contour, f"{decision} | ratio {ratio:.3f}"),
    ])


gap = np.full((10, 520 * 3, 3), 255, np.uint8)               # 줄 사이 흰 여백 (ROI 폭 520 × 3장)

rule_sheet = cv2.vconcat([make_row("ok_01"), gap, make_row("ng_01")])   # Rule 만들기용 한 쌍
test_sheet = cv2.vconcat([make_row("ok_02"), gap, make_row("ng_02")])   # Rule 확인용 한 쌍
cv2.imwrite(str(output_dir / "compare_rule_ok01_ng01.jpg"), rule_sheet)
cv2.imwrite(str(output_dir / "compare_test_ok02_ng02.jpg"), test_sheet)
print("비교 이미지 저장: compare_rule_ok01_ng01.jpg · compare_test_ok02_ng02.jpg")