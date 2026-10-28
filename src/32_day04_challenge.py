from pathlib import Path

import cv2
import numpy as np


# --------------------------------------------------
# 0. 경로 설정 (교재 41절 뼈대 그대로)
# --------------------------------------------------
reference_path = Path("samples/day04/reference/reference_label.jpg")
challenge_dir = Path("samples/day04/challenge")
output_dir = Path("outputs/day04/challenge")
output_dir.mkdir(parents=True, exist_ok=True)

challenge_files = [
    challenge_dir / "shift.jpg",
    challenge_dir / "rotate.jpg",
    challenge_dir / "distance.jpg",
    challenge_dir / "tilt_glare.jpg",
]


# --------------------------------------------------
# 1. 사용할 방법 선택
#    TEMPLATE / ORB / SIFT / SIFT_HOMOGRAPHY 중 하나
#    → 근접 사진 · 크기/회전 변화 · Template보다 작은 사진이 있어
#      SIFT_HOMOGRAPHY를 선택 (reports/day04_method_selection.md)
# --------------------------------------------------
selected_method = "SIFT_HOMOGRAPHY"

if selected_method != "SIFT_HOMOGRAPHY":
    raise ValueError("이 파일은 SIFT_HOMOGRAPHY만 구현했습니다.")


# --------------------------------------------------
# 2. Reference 읽기 → SIFT 특징점 만들기 (30번 4~6과 같음)
# --------------------------------------------------
reference = cv2.imread(str(reference_path))
if reference is None:
    raise FileNotFoundError(reference_path)

reference_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT_create()
reference_keypoints, reference_descriptors = sift.detectAndCompute(
    reference_gray, None
)
print("Reference Keypoints:", len(reference_keypoints))

# SIFT Descriptor는 L2 거리로 비교
matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

# Homography로 옮길 Reference의 네 모서리
reference_h, reference_w = reference_gray.shape[:2]
reference_corners = np.float32([
    [0, 0],
    [reference_w - 1, 0],
    [reference_w - 1, reference_h - 1],
    [0, reference_h - 1],
]).reshape(-1, 1, 2)


# --------------------------------------------------
# 3. Challenge 사진을 하나씩 검사
# --------------------------------------------------
for target_path in challenge_files:

    target = cv2.imread(str(target_path))
    if target is None:
        print("읽기 실패:", target_path)
        continue

    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    height, width = target_gray.shape[:2]

    # 사진 크기가 제각각 → 선 굵기와 글자 크기를 사진 너비에 맞춤
    line_thickness = max(3, width // 300)
    font_scale = max(0.6, width / 1400)

    # 3-1. Target에서도 SIFT 특징점 만들기
    target_keypoints, target_descriptors = sift.detectAndCompute(
        target_gray, None
    )

    # 3-2. Ratio Test로 Good Match만 남기기
    good_matches = []
    if target_descriptors is not None:
        for candidate in matcher.knnMatch(
            reference_descriptors, target_descriptors, k=2
        ):
            if len(candidate) < 2:
                continue
            m, n = candidate
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

    inlier_count = 0
    inlier_ratio = 0.0
    status = "NOT_FOUND"
    preview = target.copy()

    # 3-3. Good Match 4개 이상이면 RANSAC + Homography
    if len(good_matches) >= 4:
        reference_points = np.float32([
            reference_keypoints[m.queryIdx].pt for m in good_matches
        ]).reshape(-1, 1, 2)
        target_points = np.float32([
            target_keypoints[m.trainIdx].pt for m in good_matches
        ]).reshape(-1, 1, 2)

        homography, inlier_mask = cv2.findHomography(
            reference_points, target_points, cv2.RANSAC, 5.0
        )

        if homography is not None and inlier_mask is not None:
            inlier_count = int(inlier_mask.ravel().sum())
            inlier_ratio = inlier_count / len(good_matches)

            # Reference 네 모서리 → Target 위치로 옮겨 사각형 그리기
            projected = cv2.perspectiveTransform(reference_corners, homography)
            cv2.polylines(preview, [np.int32(projected)], True,
                          (0, 255, 0), line_thickness, cv2.LINE_AA)
            status = "FOUND"

    # 3-4. 측정값을 이미지에 쓰고 저장
    cv2.putText(
        preview,
        f"good={len(good_matches)} inlier={inlier_count} ratio={inlier_ratio:.2f}",
        (10, int(30 * font_scale) + 5),
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2, cv2.LINE_AA,
    )
    output_path = output_dir / f"{target_path.stem}_{selected_method.lower()}.jpg"
    cv2.imwrite(str(output_path), preview)

    print(
        f"{target_path.name:15s}",
        f"size={width}x{height}",
        f"good={len(good_matches)}",
        f"inlier={inlier_count}",
        f"ratio={inlier_ratio:.3f}",
        f"status={status}",
    )

print()
print("결과 이미지:", output_dir)