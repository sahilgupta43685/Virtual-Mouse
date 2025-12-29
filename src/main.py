import cv2
import numpy as np
import pyautogui
import time
from hand_detector import HandDetector

# --- CONFIGURATION ---
width_cam, height_cam = 640, 480
frame_reduction = 100
smoothening = 5

# --- SETUP ---
cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

detector = HandDetector(max_hands=1)
screen_w, screen_h = pyautogui.size()

plocX, plocY = 0, 0
clocX, clocY = 0, 0
dragging = False

while True:
    # 1. Get Frame
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)

    # 2. Detect Hand
    img = detector.find_hands(img)
    lm_list = detector.find_position(img)

    if len(lm_list) != 0:
        x1, y1 = lm_list[8][1:] # Index Tip
        fingers = detector.fingers_up() # [Thumb, Index, Middle, Ring, Pinky]

        # Draw Control Area
        cv2.rectangle(img, (frame_reduction, frame_reduction),
                      (width_cam - frame_reduction, height_cam - frame_reduction),
                      (255, 0, 255), 2)

        # --- MODE: MOVING (Index Up Only) ---
        if fingers[1] and not fingers[2]:
            # Convert Coordinates
            x3 = np.interp(x1, (frame_reduction, width_cam - frame_reduction), (0, screen_w))
            y3 = np.interp(y1, (frame_reduction, height_cam - frame_reduction), (0, screen_h))

            # Smoothen
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            
            # Move Mouse
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY

            # Check Click (Index + Thumb)
            length, img, _ = detector.find_distance(8, 4, img)
            if length < 30:
                cv2.circle(img, (lm_list[4][1], lm_list[4][2]), 15, (0, 255, 0), cv2.FILLED)
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

        # --- MODE: SCROLLING (Index + Middle Up) ---
        if fingers[1] and fingers[2]:
            length, img, _ = detector.find_distance(8, 12, img)
            if length < 40:
                if y1 < height_cam // 2: pyautogui.scroll(20)
                else: pyautogui.scroll(-20)

    # 3. Display
    cv2.imshow("Production AI Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break