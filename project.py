from ultralytics import YOLO
import cv2
import pyttsx3
import time

# Load YOLO model
model = YOLO("yolov8n.pt")

# Initialize voice engine
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Open camera
cap = cv2.VideoCapture(0)

# Timers
last_time = 0

# Analytics counters
object_count = 0
person_count = 0
hazard_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_width = frame.shape[1]

    # ---------------------------
    # 🔍 Object Detection
    # ---------------------------
    results = model(frame)

    detected_objects = []
    directions = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            # Bounding box center
            x1, y1, x2, y2 = box.xyxy[0]
            center_x = (x1 + x2) / 2

            # Direction logic
            if center_x < frame_width / 3:
                direction = "left"
            elif center_x > 2 * frame_width / 3:
                direction = "right"
            else:
                direction = "center"

            detected_objects.append(label)
            directions.append((label, direction))

    # Update analytics
    object_count += len(detected_objects)

    if "person" in detected_objects:
        person_count += 1

    # ---------------------------
    # ⚠️ Hazard Detection
    # ---------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = gray.mean()

    if brightness < 40:
        hazard_count += 1
        if time.time() - last_time > 5:
            speak("Warning. Low visibility detected")
            last_time = time.time()

    # ---------------------------
    # 👤 Human Awareness
    # ---------------------------
    for obj, dir in directions:
        if obj == "person" and time.time() - last_time > 5:
            speak(f"Person on your {dir}")
            last_time = time.time()
            break

    # ---------------------------
    # 🔊 Object + Direction Speech
    # ---------------------------
    if directions and time.time() - last_time > 5:
        obj, dir = directions[0]
        speak(f"{obj} detected on your {dir}")
        last_time = time.time()

    # ---------------------------
    # 📊 Print Analytics (Live)
    # ---------------------------
    print(f"Objects: {object_count} | Persons: {person_count} | Hazards: {hazard_count}")

    # ---------------------------
    # 🖥️ Display Output
    # ---------------------------
    annotated_frame = results[0].plot()
    cv2.imshow("VisionMate AI", annotated_frame)

    # Exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()