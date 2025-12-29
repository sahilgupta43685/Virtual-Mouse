import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import math
import time
import speech_recognition as sr

# --- CONFIGURATION ---
width_cam, height_cam = 640, 480
frame_reduction = 100
smoothening = 5

# --- CLASS: HAND DETECTOR ---
class HandDetector:
    def __init__(self, mode=False, max_hands=1, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
        return self.lm_list

    def fingers_up(self):
        fingers = []
        if len(self.lm_list) == 0: return fingers
        
        # Thumb (Right Hand Logic)
        if self.lm_list[self.tip_ids[0]][1] < self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(True)
        else:
            fingers.append(False)
            
        # 4 Fingers
        for id in range(1, 5):
            if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(True)
            else:
                fingers.append(False)
        return fingers

    def find_distance(self, p1, p2, img=None):
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        if img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return length, img, [x1, y1, x2, y2, cx, cy]

# --- MAIN SETUP ---
cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

detector = HandDetector(max_hands=1)
screen_w, screen_h = pyautogui.size()

# Variables
plocX, plocY = 0, 0
clocX, clocY = 0, 0
dragging = False
pTime = 0
last_click_time = 0

# --- VOICE SETUP ---
r = sr.Recognizer()
mic = sr.Microphone()
print("Adjusting microphone noise... Please wait.")
with mic as source:
    r.adjust_for_ambient_noise(source)
print("System Ready!")

while True:
    # 1. Get Frame
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)

    # 2. Detect Hand
    img = detector.find_hands(img)
    lm_list = detector.find_position(img)
    
    # Draw Control Box
    cv2.rectangle(img, (frame_reduction, frame_reduction),
            (width_cam - frame_reduction, height_cam - frame_reduction), 
            (255, 0, 255), 2)
    
    mode_text = "Idle" # Default status

    if len(lm_list) != 0:
        x1, y1 = lm_list[8][1:] # Index Tip
        fingers = detector.fingers_up() # [Thumb, Index, Middle, Ring, Pinky]

        # --- MODE 1: MOVING & CLICKING (Index Up, Middle Down) ---
        if fingers[1] and not fingers[2] and not fingers[4]:
            mode_text = "Moving Mode"
            
            # Coordinate Conversion
            x3 = np.interp(x1, (frame_reduction, width_cam - frame_reduction), (0, screen_w))
            y3 = np.interp(y1, (frame_reduction, height_cam - frame_reduction), (0, screen_h))

            # Smoothening
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            
            pyautogui.moveTo(clocX, clocY)
            plocX, plocY = clocX, clocY

            # Click Check (Index + Thumb)
            length, img, line_info = detector.find_distance(8, 4, img)
            
            # Visual Feedback for Click
            if length < 30:
                cv2.circle(img, (line_info[4], line_info[5]), 15, (0, 255, 0), cv2.FILLED) # Green
                mode_text = "Click / Drag"
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

        # --- MODE 2: SCROLLING (Index + Middle Up) ---
        if fingers[1] and fingers[2]:
            mode_text = "Scroll Mode"
            length, img, _ = detector.find_distance(8, 12, img)
            if length < 40:
                if y1 < height_cam // 2: 
                    pyautogui.scroll(20)
                    cv2.putText(img, "UP", (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
                else: 
                    pyautogui.scroll(-20)
                    cv2.putText(img, "DOWN", (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)

        # --- MODE 3: VOICE TYPING (Pinky Up Only) ---
        if fingers[4] and not fingers[1] and not fingers[2]:
            mode_text = "Listening..."
            cv2.circle(img, (lm_list[20][1], lm_list[20][2]), 15, (0, 0, 255), cv2.FILLED)
            
            # Force update display before listening
            cv2.putText(img, f'Mode: {mode_text}', (10, height_cam - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Advanced AI Mouse", img)
            cv2.waitKey(1)

            try:
                with mic as source:
                    audio = r.listen(source, timeout=2, phrase_time_limit=5)
                    command = r.recognize_google(audio)
                    print(f"User said: {command}")
                    pyautogui.write(command + " ") 
            except Exception as e:
                print("Voice Error/Timeout")

        # --- MODE 4: ENTER KEY (Fist / All Fingers Down) ---
        if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            mode_text = "Enter Key"
            if time.time() - last_click_time > 1:
                pyautogui.press('enter')
                last_click_time = time.time()
                cv2.putText(img, "ENTER PRESSED", (width_cam//2 - 100, height_cam//2), 
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 3)

    # --- FPS & HUD ---
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Status Bar
    cv2.rectangle(img, (0, height_cam - 40), (width_cam, height_cam), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, f'Mode: {mode_text}', (10, height_cam - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Display
    cv2.imshow("Advanced AI Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()