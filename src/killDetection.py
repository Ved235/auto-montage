import cv2
from ultralytics import YOLO
import os

def detectKills(video_path, model_path='./model.pt'):
    timestamps = []
    model = YOLO(model_path)
    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS)
    count = 0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        if count % 10 == 0:
            results = model(frame)

            result = results[0].boxes

            for box in result:
                timestamps.append(count / fps)
        count += 1
    
    capture.release()
    print("Timestamps of kills detected")
    return timestamps

if __name__ == "__main__":
    video_path = "./test.mp4"
    model_path = "./model.pt"
    if not os.path.exists(model_path):
        print(f"Model file {model_path} does not exist.")
    else:
        kill_timestamps = detectKills(video_path, model_path)
        print(kill_timestamps)