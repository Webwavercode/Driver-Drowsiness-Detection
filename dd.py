import cv2
import numpy as np
import winsound
import threading
import time

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

sleep, drowsy, active = 0, 0, 0
status, color = "", (0, 0, 0)

beep_flag = False
beep_thread = None

def beep_continuous():
    while beep_flag:
        winsound.Beep(1000, 1000)

def beep_multiple(times):
    for _ in range(times):
        winsound.Beep(1000, 500)
        time.sleep(0.5)

def start_continuous_beep():
    global beep_thread
    beep_flag = True
    if not beep_thread or not beep_thread.is_alive():
        beep_thread = threading.Thread(target=beep_continuous)
        beep_thread.start()

def stop_continuous_beep():
    global beep_flag
    beep_flag = False
    if beep_thread and beep_thread.is_alive():
        beep_thread.join()

def blinked(eyes):
    return 0 if len(eyes) == 0 else 1 if len(eyes) == 1 else 2

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        left_blink, right_blink = blinked(eyes), blinked(eyes)

        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy, active = 0, 0
            if sleep > 6:
                status, color = "SLEEPING !!!", (255, 0, 0)
                start_continuous_beep()
        elif left_blink == 1 or right_blink == 1:
            sleep, active = 0, 0
            drowsy += 1
            if drowsy > 6:
                status, color = "Drowsy !", (0, 0, 255)
                stop_continuous_beep()
                threading.Thread(target=beep_multiple, args=(4,)).start()
        else:
            sleep, drowsy = 0, 0
            active += 1
            if active > 6:
                status, color = "Active :)", (0, 255, 0)
                stop_continuous_beep()

        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
stop_continuous_beep()
