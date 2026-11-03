# ==================================================
# day08_mini_challenge.py
# 본 실습(broken_small)의 Cut-Paste 흐름을
# contamination 결함에 다시 적용하는 Mini Challenge
# ==================================================
from pathlib import Path

from day08_cutpaste_core import (
    generate_synthetic_set,   # 69번과 같은 공통 함수 재사용
)

# --------------------------------------------------
# ① 입력 경로 — 63번이 Mini Challenge용으로 따로 나눠 둔 데이터
#    (본 실습·Query와 겹치지 않는 이미지)
# --------------------------------------------------
NORMAL_DIR = Path("samples/day08/mini_challenge/normal")
DEFECT_ROOT = Path("samples/day08/mini_challenge/defect_source/contamination")

# --------------------------------------------------
# ② 출력 경로 — 본 실습 결과와 섞이지 않게 별도 폴더
# --------------------------------------------------
OUTPUT_DIR = Path("outputs/day08/mini_challenge/generated")
METADATA_PATH = Path("reports/day08_mini_challenge_metadata.csv")

# --------------------------------------------------
# ③ 교재 48절 조건으로 Synthetic Defect 생성
# --------------------------------------------------
rows = generate_synthetic_set(
    normal_dir=NORMAL_DIR,
    defect_image_dir=DEFECT_ROOT / "images",   # 오염 원본 2장
    defect_mask_dir=DEFECT_ROOT / "masks",     # 짝이 되는 GT Mask 2장
    output_dir=OUTPUT_DIR,
    metadata_path=METADATA_PATH,
    defect_type="contamination",
    count=5,                     # 5장만
    seed=42,                     # 다시 돌려도 같은 결과
    scale_range=(0.6, 1.0),      # 본 실습보다 작게 (너무 큰 결함 줄이기)
    angle_range=(-10.0, 10.0),   # 본 실습보다 회전 폭 작게
)

# --------------------------------------------------
# ④ 결과 확인
# --------------------------------------------------
print("=" * 70)
print("DAY08 MINI CHALLENGE — CONTAMINATION CUT-PASTE")
print("=" * 70)
print("Defect Type      : contamination")
print("Generated Images :", len(rows))
print("Output           :", OUTPUT_DIR)
print("Metadata         :", METADATA_PATH)