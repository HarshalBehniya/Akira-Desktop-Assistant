 # Akira Desktop Assistant 🧠🎙️

Akira is a powerful voice and text-based AI desktop assistant built using Python. It provides intelligent system control, productivity tools, YouTube/Google integration, reminders, WhatsApp messaging, and much more — all from a sleek GUI interface.

---

## 🚀 Features

- 🎤 **Voice and Text Input** modes
- 🔔 **Smart Reminders** (absolute & relative time)
- ⏰ **Alarm with voice stop**
- 📹 **Video & Screen Recording**
- 📝 **Note taking + To-do list management**
- 📷 **Selfie and Screenshot capture**
- 🎬 **YouTube Controls**: Play, pause, next, previous
- 🌐 **Google Search + ChatGPT Search**
- 💻 **System control**: Shutdown, restart, lock, etc.
- 💬 **Send WhatsApp messages automatically**
- 🧹 **PC Cleanup tools**
- 👁️ **Face registration and detection**
- 🧠 **Contextual Memory** for follow-up commands

---

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

git clone https://github.com/HarshalBehniya/Akira-Desktop-Assistant.git

cd Akira-Desktop-Assistant

2. Create & Activate Virtual Environment (optional but recommended)

python -m venv venv
venv\Scripts\activate   # Windows

3. Install Dependencies

pip install -r requirements.txt

4. Download ChromeDriver
Make sure ChromeDriver is installed and added to your system path. Version should match your Chrome browser.

▶️ How to Run

python akira_app.py

---

---

📁 Project Structure

akira_app.py            # GUI application

akira_engine.py         # All backend logic and handlers

data/                   # Screenshots, reminders, notes, face data

requirements.txt        # Python dependencies

README.md               # This file

---

---

💬 Example Voice Commands

Remind me to drink water at 4 PM

Play lofi beats on YouTube

Set alarm for 7 AM

Note Buy groceries

Register my face as Harshal

Message Sahil saying Hello

Clean my PC

Search Google for Python tutorials

---

---


🤖 Tech Stack

Python 3.10+

Tkinter – GUI

SpeechRecognition, PyAudio – Voice input

PyAutoGUI, OpenCV, pyttsx3 – Interaction & automation

Selenium – WhatsApp automation

Face recognition – Face registration & lock screen

Threading – Efficient reminders and real-time response

---

---

💡 Credits
Created with 💻 by Harshal Behniya

---
