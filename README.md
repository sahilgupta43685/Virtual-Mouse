# Touchless HMI Gesture Control System 🚗

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-orange?style=for-the-badge)

> **A multimodal Human-Machine Interface (HMI) prototype designed to simulate hands-free automotive cockpit controls using Computer Vision and Voice Recognition.**

---

## 📖 Project Overview
In modern automotive environments, driver safety is paramount. Physical touchscreens can be distracting. This project engineers a **Touchless Interface** that allows users to control digital systems using intuitive hand gestures and voice commands, eliminating the need for physical contact.

Key engineering goals achieved:
* **<50ms Latency:** Real-time tracking optimized for rapid interaction.
* **Multimodal Input:** "Sensor Fusion" of visual gestures and auditory commands.
* **Precision Smoothing:** Implemented Exponential Moving Average (EMA) to stabilize cursor movement against vibration/noise.

---

## ⚙️ System Architecture
The system operates on a dual-thread pipeline:
1.  **Vision Engine:** Uses Google MediaPipe to track 21 hand landmarks. Coordinates are mapped to the screen using linear interpolation.
2.  **Voice Engine:** Listens for wake-word gestures ("Pinky Up") to trigger the Google Speech-to-Text API for natural language input.



---

## 🚀 Key Features

| Feature | Gesture / Trigger | Description |
| :--- | :--- | :--- |
| **Cursor Navigation** | 👆 Index Up | Smooth, jitter-free cursor tracking. |
| **Click & Drag** | 👌 Pinch (Index + Thumb) | Left click. Hold pinch to drag items. |
| **Smart Scrolling** | ✌️ Index + Middle Up | Move hand up/down to scroll pages. |
| **Voice Typing** | 🤙 Pinky Up | Activates microphone. Speaks to type. |
| **"Enter" Key** | ✊ Fist | Simulates pressing the physical 'Enter' key. |
| **Visual HUD** | *On Screen* | Real-time FPS counter, Mode Status, and Laser tracking lines. |

---

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Core Libraries:**
    * `OpenCV` - Image processing & video capture.
    * `MediaPipe` - Machine Learning pipeline for hand tracking.
    * `PyAutoGUI` - System automation (Mouse/Keyboard events).
    * `SpeechRecognition` - NLP integration for voice commands.
    * `NumPy` - Mathematical operations for coordinate interpolation.

