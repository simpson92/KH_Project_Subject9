from pathlib import Path

# 5일차 공통 측정 함수 재사용 (광천김과 같은 함수, Reference만 바뀜)
from day05_logo_features import (
    prepare_reference,
    measure_target,
)

# --------------------------------------------------
# 0. 경로 설정 (교재 35절 뼈대 그대로)
# --------------------------------------------------
ROOT = Path("samples/day05/mini_challenge")
REFERENCE_PATH = ROOT / "reference/reference_label.jpg"
CALIBRATION_DIR = ROOT / "calibration"
TEST_DIR = ROOT / "test"


# --------------------------------------------------
# 1. Reference 준비 (SIFT 특징점을 한 번만 계산)
# --------------------------------------------------
reference_data = prepare_reference(REFERENCE_PATH)
print("Reference:", REFERENCE_PATH)
print("Reference 크기:", reference_data["width"], "x", reference_data["height"])
print("Reference Keypoints:", len(reference_data["keypoints"]))


# --------------------------------------------------
# 2. Smoke Test — Calibration OK 한 장만 먼저 측정
#    (12장 · 6장을 한꺼번에 돌리기 전에 동작 확인)
# --------------------------------------------------
sample_path = CALIBRATION_DIR / "ok" / "ok_01.jpg"
m = measure_target(sample_path, reference_data)

print()
print("=" * 50)
print("Smoke Test:", sample_path.name)
print(f"Template Score   : {m['template_score']:.4f}")
print(f"SIFT Good Match  : {m['sift_good_matches']}")
print(f"Homography Found : {m['homography_found']}")
print(f"Homography Inlier: {m['homography_inliers']}")
print(f"Inlier Ratio     : {m['inlier_ratio']:.4f}")
print("=" * 50)

# --------------------------------------------------
# 3. Calibration OK 3장 + NG 3장 측정 → CSV 저장 (34번 방식)
#    Test 이미지는 아직 사용하지 않음
# --------------------------------------------------
import csv

CAL_CSV = Path("reports/day05_mini_calibration_measurements.csv")

rows = []
for actual in ["OK", "NG"]:
    folder = CALIBRATION_DIR / actual.lower()            # calibration/ok , calibration/ng
    for image_path in sorted(folder.glob("*.jpg")):
        m = measure_target(image_path, reference_data)    # 모든 사진에 같은 조건
        rows.append({
            "file": image_path.name,
            "actual": actual,                              # 사람이 아는 정답
            "template_score": round(m["template_score"], 6),
            "sift_good_matches": m["sift_good_matches"],
            "homography_found": m["homography_found"],
            "homography_inliers": m["homography_inliers"],
            "inlier_ratio": round(m["inlier_ratio"], 6),
        })

CAL_CSV.parent.mkdir(parents=True, exist_ok=True)
with CAL_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print()
print(f"{'file':10s} {'actual':6s} {'Template':>8s} {'SIFT':>5s} {'Inlier':>6s} {'Ratio':>7s}")
for r in rows:
    print(f"{r['file']:10s} {r['actual']:6s} {r['template_score']:8.4f} "
          f"{r['sift_good_matches']:5d} {r['homography_inliers']:6d} {r['inlier_ratio']:7.4f}")
print()
print("Calibration 측정 완료:", len(rows), "장 →", CAL_CSV)

# --------------------------------------------------
# 4. Threshold 후보 시험 (35번 방식) — 두 가지 Feature 조합 비교
#    Rule 모양: Homography 성공 AND 특징1 >= ? AND 특징2 >= ?  → OK
# --------------------------------------------------
import numpy as np


def make_candidates(values, count=15, integer=False):
    """최솟값~최댓값을 count칸으로 나눈 Threshold 후보 (35번과 같은 방식)"""
    low, high = min(values), max(values)
    if low == high:
        return [low]
    cands = np.linspace(low, high, count)
    if integer:
        return sorted(set(int(round(v)) for v in cands))
    return sorted(set(round(float(v), 4) for v in cands))


def search_rules(rows, key1, key2, int1, int2):
    c1 = make_candidates([r[key1] for r in rows], integer=int1)
    c2 = make_candidates([r[key2] for r in rows], integer=int2)
    results = []
    for t1 in c1:
        for t2 in c2:
            tp = tn = fp = fn = 0
            for r in rows:
                ok = r["homography_found"] == 1 and r[key1] >= t1 and r[key2] >= t2
                pred = "OK" if ok else "NG"
                if r["actual"] == "NG" and pred == "NG": tp += 1
                elif r["actual"] == "OK" and pred == "OK": tn += 1
                elif r["actual"] == "OK" and pred == "NG": fp += 1
                else: fn += 1
            results.append({key1: t1, key2: t2,
                            "accuracy": round((tp + tn) / len(rows), 4),
                            "tp": tp, "tn": tn, "fp": fp, "fn": fn, "total_error": fp + fn})
    # FN이 적은 순 → 전체 오류 → FP → 작은 기준값 순 (35번 정렬 규칙)
    results.sort(key=lambda x: (x["fn"], x["total_error"], x["fp"], x[key1], x[key2]))
    return results, len(c1) * len(c2)


pairs = [
    ("sift_good_matches", "inlier_ratio", True, False),        # 조합 A (광천김과 같음)
    ("sift_good_matches", "homography_inliers", True, True),   # 조합 B
]

CAND_CSV = Path("reports/day05_mini_rule_candidates.csv")
all_rows = []
for key1, key2, int1, int2 in pairs:
    results, n = search_rules(rows, key1, key2, int1, int2)
    print()
    print("=" * 70)
    print(f"조합: {key1} + {key2}  (시험한 조합 {n}개) · 상위 5개")
    print("=" * 70)
    for r in results[:5]:
        print(f"{key1} >= {r[key1]:<7} {key2} >= {r[key2]:<7} "
              f"Acc {r['accuracy']:.4f}  TP {r['tp']} TN {r['tn']} FP {r['fp']} FN {r['fn']}")
    for r in results:
        all_rows.append({"pair": f"{key1}+{key2}", "t1": r[key1], "t2": r[key2],
                         **{k: r[k] for k in ["accuracy", "tp", "tn", "fp", "fn", "total_error"]}})

with CAND_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
    writer.writeheader()
    writer.writerows(all_rows)
print()
print("후보 저장:", CAND_CSV)

# --------------------------------------------------
# 5. Rule Freeze (36번 방식) — 고른 값을 그대로 JSON에 저장
#    ※ Threshold를 다시 탐색하지 않음. 이 값은 Test에서 바꾸지 않음
# --------------------------------------------------
import json

RULE_PATH = Path("configs/day05_mini_rules.json")

rule = {
    "baseline_version": "day05-mini-v1.0",
    "inspection_target": "드림카카오 72% 노란 라벨 존재 및 정합 검사",
    "positive_class": "NG",
    "reference": {"reference_label": str(REFERENCE_PATH)},
    "required_rules": {
        "homography_found": True,
        "sift_good_matches_min": 44,
        "inlier_ratio_min": 0.6657,
    },
    "calibration_result": {"accuracy": 0.6667, "tp": 3, "tn": 1, "fp": 2, "fn": 0},
    "note": "Calibration 6장(OK 3 · NG 3)으로 35번 방식 1위 후보를 선택. SIFT 기준은 최솟값이라 사실상 Ratio가 판정",
}

RULE_PATH.parent.mkdir(parents=True, exist_ok=True)
with RULE_PATH.open("w", encoding="utf-8") as f:
    json.dump(rule, f, ensure_ascii=False, indent=2)

print()
print("=" * 70)
print("Rule 동결 완료:", RULE_PATH, "·", rule["baseline_version"])
print("SIFT >=", rule["required_rules"]["sift_good_matches_min"],
      "AND Inlier Ratio >=", rule["required_rules"]["inlier_ratio_min"])
print("=" * 70)

# --------------------------------------------------
# 6. Test — 동결한 JSON을 다시 읽어서 Test 4장에 그대로 적용 (37번 방식)
#    ※ 여기서 나온 결과를 보고 기준을 바꾸지 않음
# --------------------------------------------------
import cv2

TEST_CSV = Path("reports/day05_mini_test_results.csv")
TEST_OUT_DIR = Path("outputs/day05/mini_test")
TEST_OUT_DIR.mkdir(parents=True, exist_ok=True)

# 위의 rule 변수가 아니라 "파일"에서 읽음 → 저장된 기준만 사용한다는 증거
with RULE_PATH.open("r", encoding="utf-8") as f:
    frozen = json.load(f)
req = frozen["required_rules"]


def judge(m):
    """측정값 m을 JSON 기준과 비교해 (판정, 이유 목록)을 돌려줌"""
    reasons = []
    if req["homography_found"] and m["homography_found"] != 1:
        reasons.append("HOMOGRAPHY_NOT_FOUND")
    if m["sift_good_matches"] < req["sift_good_matches_min"]:
        reasons.append("LOW_SIFT_MATCH")
    if m["inlier_ratio"] < req["inlier_ratio_min"]:
        reasons.append("LOW_INLIER_RATIO")
    return ("NG" if reasons else "OK"), reasons


test_rows = []
for actual in ["ok", "ng"]:
    for path in sorted((TEST_DIR / actual).glob("*.jpg")):
        m = measure_target(path, reference_data)
        predicted, reasons = judge(m)

        # 결과 이미지: 사각형 색 = 프로그램 판정 (초록 OK / 빨강 NG)
        img = m["target_image"].copy()
        color = (0, 255, 0) if predicted == "OK" else (0, 0, 255)
        if m["polygon"] is not None:
            pts = np.int32(m["polygon"]).reshape(-1, 1, 2)
            cv2.polylines(img, [pts], True, color, 5)
        text = f"Actual {actual.upper()} / Pred {predicted}  Ratio {m['inlier_ratio']:.4f}"
        cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.imwrite(str(TEST_OUT_DIR / f"{path.stem}_result.jpg"), img)

        test_rows.append({
            "file": path.name,
            "actual": actual.upper(),
            "predicted": predicted,
            "sift_good_matches": m["sift_good_matches"],
            "homography_inliers": m["homography_inliers"],
            "inlier_ratio": round(m["inlier_ratio"], 4),
            "ng_reason": ";".join(reasons) if reasons else "-",
        })

with TEST_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=test_rows[0].keys())
    writer.writeheader()
    writer.writerows(test_rows)

print()
print("=" * 70)
print("Test 판정 (Rule:", frozen["baseline_version"], ")")
print("=" * 70)
print(f"{'file':<16}{'actual':>7}{'pred':>6}{'SIFT':>6}{'Ratio':>9}  reason")
for r in test_rows:
    print(f"{r['file']:<16}{r['actual']:>7}{r['predicted']:>6}"
          f"{r['sift_good_matches']:>6}{r['inlier_ratio']:>9}  {r['ng_reason']}")
print()
print("Test 결과 저장:", TEST_CSV, "· 이미지:", TEST_OUT_DIR)

# --------------------------------------------------
# 7. 성능 계산 (38번 방식) — NG가 Positive
# --------------------------------------------------
METRICS_MD = Path("reports/day05_mini_test_metrics.md")

tp = sum(r["actual"] == "NG" and r["predicted"] == "NG" for r in test_rows)  # 불량을 불량으로
tn = sum(r["actual"] == "OK" and r["predicted"] == "OK" for r in test_rows)  # 정상을 정상으로
fp = sum(r["actual"] == "OK" and r["predicted"] == "NG" for r in test_rows)  # 정상을 불량으로 (과검출)
fn = sum(r["actual"] == "NG" and r["predicted"] == "OK" for r in test_rows)  # 불량을 정상으로 (미검출)

total = len(test_rows)
accuracy = (tp + tn) / total
precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0   # NG라고 한 것 중 진짜 NG 비율
recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0      # 진짜 NG 중 찾아낸 비율

# 틀린 이미지 이름 모으기 → 실패 분석 재료
fp_files = [r["file"] for r in test_rows if r["actual"] == "OK" and r["predicted"] == "NG"]
fn_files = [r["file"] for r in test_rows if r["actual"] == "NG" and r["predicted"] == "OK"]

print()
print("=" * 70)
print(f"TP {tp}  TN {tn}  FP {fp}  FN {fn}  (전체 {total}장)")
print(f"Accuracy {accuracy:.4f}  Precision {precision:.4f}  Recall {recall:.4f}")
print("FP 이미지:", fp_files if fp_files else "없음")
print("FN 이미지:", fn_files if fn_files else "없음")
print("=" * 70)

with METRICS_MD.open("w", encoding="utf-8") as f:
    f.write(f"# Day05 Mini Challenge Test Metrics ({frozen['baseline_version']})\n\n")
    f.write("| TP | TN | FP | FN | Accuracy | Precision | Recall |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    f.write(f"| {tp} | {tn} | {fp} | {fn} | {accuracy:.4f} | {precision:.4f} | {recall:.4f} |\n\n")
    f.write(f"- FP: {', '.join(fp_files) if fp_files else '없음'}\n")
    f.write(f"- FN: {', '.join(fn_files) if fn_files else '없음'}\n")

print("성능 저장:", METRICS_MD)