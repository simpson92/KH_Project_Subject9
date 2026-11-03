# ==================================================
# day08_support_count_challenge.py
# Few-shot Support 수(1 · 3 · 5장)를 바꿔
# 같은 Common Query 20장에서 성능을 비교하는 Challenge
# ==================================================
import csv
from pathlib import Path

from day08_feature_core import (
    build_prototype,       # 여러 Feature 평균 → 길이 1 Prototype
    cosine_similarity,     # 두 Feature의 Cosine Similarity
    create_feature_model,  # 사전학습 ResNet18 (fc 제외, 512-D)
    extract_feature,       # 이미지 1장 → Feature
)

# --------------------------------------------------
# ① 경로와 실험 조건
# --------------------------------------------------
SUPPORT_ROOT = Path("samples/day08/few_shot/support")
QUERY_ROOT = Path("samples/day08/common_query")
CSV_PATH = Path("reports/day08_support_count_challenge.csv")

SUPPORT_COUNTS = [1, 3, 5]   # 바꾸는 조건은 이것 하나

model = create_feature_model()

# --------------------------------------------------
# ② Support 이미지 목록 (이름순 정렬 → 항상 같은 순서)
#    1장 = 앞 1장, 3장 = 앞 3장, 5장 = 전체
# --------------------------------------------------
normal_files = sorted((SUPPORT_ROOT / "normal").glob("*.png"))
anomaly_files = sorted((SUPPORT_ROOT / "anomaly").glob("*.png"))

if len(normal_files) < max(SUPPORT_COUNTS) or len(anomaly_files) < max(SUPPORT_COUNTS):
    raise RuntimeError("Support 이미지가 5장보다 적습니다. 63번을 먼저 확인하세요.")

# Support Feature를 미리 한 번만 추출 (장수만 잘라서 재사용)
normal_features = [extract_feature(model, p) for p in normal_files]
anomaly_features = [extract_feature(model, p) for p in anomaly_files]

# --------------------------------------------------
# ③ Common Query 20장 Feature도 한 번만 추출
#    (Support 수가 바뀌어도 Query는 그대로)
# --------------------------------------------------
queries = []   # (sample_id, actual, feature)

for path in sorted((QUERY_ROOT / "normal").glob("*.png")):
    queries.append((f"normal/{path.name}", "Normal", extract_feature(model, path)))

for path in sorted((QUERY_ROOT / "anomaly" / "broken_small").glob("*.png")):
    queries.append((f"anomaly/broken_small/{path.name}", "Anomaly", extract_feature(model, path)))

# --------------------------------------------------
# ④ Support 수마다 Prototype을 새로 만들고 같은 Query 검사
# --------------------------------------------------
rows = []

for k in SUPPORT_COUNTS:
    # 앞에서 k장만 사용해 Prototype 생성
    normal_prototype = build_prototype(normal_features[:k])
    anomaly_prototype = build_prototype(anomaly_features[:k])

    tp = tn = fp = fn = 0
    wrong = []   # 틀린 sample_id 기록

    for sample_id, actual, feature in queries:
        normal_sim = cosine_similarity(feature, normal_prototype)
        anomaly_sim = cosine_similarity(feature, anomaly_prototype)

        # 67번과 같은 판정 규칙: 정상 쪽이 같거나 더 가까우면 Normal
        predicted = "Normal" if normal_sim >= anomaly_sim else "Anomaly"

        # Positive = Anomaly
        if actual == "Anomaly" and predicted == "Anomaly":
            tp += 1
        elif actual == "Normal" and predicted == "Normal":
            tn += 1
        elif actual == "Normal" and predicted == "Anomaly":
            fp += 1
            wrong.append(f"FP:{sample_id}")
        else:
            fn += 1
            wrong.append(f"FN:{sample_id}")

    total = tp + tn + fp + fn
    rows.append({
        "support_count": k,
        "accuracy": round((tp + tn) / total, 4),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "normal_support": " ".join(p.name for p in normal_files[:k]),
        "anomaly_support": " ".join(p.name for p in anomaly_files[:k]),
        "wrong_samples": " ".join(wrong),
    })

# --------------------------------------------------
# ⑤ CSV 저장 + 화면 출력
# --------------------------------------------------
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("=" * 70)
print("DAY08 SUPPORT COUNT CHALLENGE")
print("=" * 70)
print(f"Query: {len(queries)}장 (Normal 10 + broken_small 10, 모든 실험 동일)")
print()
for row in rows:
    print(
        f"Support {row['support_count']}장 | "
        f"Acc {row['accuracy']:.4f} | FP {row['fp']} | FN {row['fn']} | "
        f"틀림: {row['wrong_samples'] or '-'}"
    )
print()
print("Saved:", CSV_PATH)