import cv2
import os

stream_url = os.environ.get(                      # 환경변수 PHONE_STREAM_URL이 있으면 그 값을,
    "PHONE_STREAM_URL",
    "http://<휴대폰_IP>:8080/video",              # 없으면 이 안내 문구를 씀 (공개돼도 안전)
)

cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("스마트폰 영상을 열 수 없습니다.")
    raise SystemExit

while True:
    ret, frame = cap.read()

    if not ret:
        print("Frame을 읽을 수 없습니다.")
        break

    cv2.imshow("Phone Camera", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()