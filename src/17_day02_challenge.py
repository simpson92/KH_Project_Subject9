from pathlib import Path
import numpy as np
import cv2


image_path = Path(
    "samples/day02/challenge.jpg"
)

output_dir = Path(
    "outputs/day02/challenge"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)


image = cv2.imread(
    str(image_path)
)

if image is None:
    raise FileNotFoundError(
        f"이미지를 읽지 못했습니다: {image_path}"
    )


# --------------------------------------------------
# TODO
#
img = image.astype(np.float32)            # 나눗셈을 하려면 정수(uint8)를 실수로 바꿔야 함
B, G, R = cv2.split(img)                  # OpenCV는 B, G, R 순서
chroma = (B - R) / (B + G + R + 1e-6)     # 파랑이 빨강보다 얼마나 많은지를 '전체 밝기 대비 비율'로 계산
                                          # 1e-6: 검은 픽셀(합이 0)에서 0으로 나누는 에러 방지
result = np.clip((chroma + 0.05) / 0.10 * 255, 0, 255).astype(np.uint8)
                                          # -0.05~+0.05 범위를 0~255로 늘리고, 벗어난 값은 잘라냄
result = cv2.medianBlur(result, 7)        # 압축 블록 노이즈 정리 (지난번과 같은 Median 7)

# --------------------------------------------------
# 전처리 결과 저장
# --------------------------------------------------

result_path = (
    output_dir
    / "challenge_result.jpg"
)

cv2.imwrite(
    str(result_path),
    result,
)


# --------------------------------------------------
# Gray 변환
# --------------------------------------------------

def to_gray(source):

    if len(source.shape) == 2:
        return source

    return cv2.cvtColor(
        source,
        cv2.COLOR_BGR2GRAY,
    )


original_gray = to_gray(
    image
)

result_gray = to_gray(
    result
)


# --------------------------------------------------
# 전처리 전 Otsu
#
# 이번 Challenge에서는
# 밝은 병뚜껑을 흰색 객체로 확인합니다.
# --------------------------------------------------

_, original_otsu = cv2.threshold(
    original_gray,
    0,
    255,
    cv2.THRESH_BINARY
    + cv2.THRESH_OTSU,
)


# --------------------------------------------------
# 전처리 후 Otsu
# --------------------------------------------------

_, result_otsu = cv2.threshold(
    result_gray,
    0,
    255,
    cv2.THRESH_BINARY
    + cv2.THRESH_OTSU,
)


cv2.imwrite(
    str(
        output_dir
        / "challenge_original_otsu.jpg"
    ),
    original_otsu,
)

cv2.imwrite(
    str(
        output_dir
        / "challenge_result_otsu.jpg"
    ),
    result_otsu,
)


print("입력 :", image_path)
print("결과 :", result_path)
print("Challenge 완료")