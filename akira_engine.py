import os
import webbrowser
# import win32com.client
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
import cv2
from urllib.parse import quote
import time
import pyautogui
import pyttsx3
import threading
# import queue
from playsound import playsound
import re
import pygetwindow as gw
import speech_recognition as sr
import json
import shutil
import ctypes
import psutil
import webbrowser
import platform 
from datetime import datetime, timedelta
# import datetime
import webbrowser
import numpy as np
from queue import Queue

# import face_recognition
from urllib.parse import quote_plus

webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files//Google//Chrome//Application//chrome.exe"))

# from utils import load_context, clear_context  

# from features.system_controls import toggle_wifi, toggle_bluetooth, toggle_airplane_mode, toggle_battery_saver

# from features.pc_cleaner import clean_temp_files, empty_recycle_bin, close_background_apps
 
from queue import Queue
import threading

speech_queue = Queue()


SAVE_FOLDER = 'akira'
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

REMINDER_FILE = "reminders.json"

# Create the reminder file if it doesn't exist
if not os.path.exists(REMINDER_FILE):
    with open(REMINDER_FILE, "w") as f:
        json.dump([], f)

engine = pyttsx3.init()
engine.setProperty("rate", 180)

speech_queue = Queue()

def say(text):
    print("Akira:", text)
    speech_queue.put(text)

def speech_worker():
    while True:
        text = speech_queue.get()
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS Error:", e)
        speech_queue.task_done()

# Start this once at the bottom of akira_engine.py
threading.Thread(target=speech_worker, daemon=True).start()
input_mode = "voice"  # default input mode


def takecommand():
    global input_mode
    if input_mode == "text":
        return input("You: ").lower()
    else:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.pause_threshold = 2  # Waits 2 sec of silence before ending

            try:
                audio = recognizer.listen(source)  # No timeout, waits for speech
                query = recognizer.recognize_google(audio)
                print("You:", query)
                return query.lower()
            except sr.UnknownValueError:
                # say("Sorry, I didn't catch that. Please repeat.")
                return ""
            except sr.RequestError:
                # say("Speech recognition service is unavailable.")
                return ""

def ensure_data_folder():
    data_folder = os.path.join(os.getcwd(), "data")
    os.makedirs(data_folder, exist_ok=True) 

ensure_data_folder()
 


def open_app(app_path):
    try:
        subprocess.Popen(app_path)
    except Exception as e:
        print(f"Error opening application: {e}")

def whatsapp_message(name, message):
    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\\Users\\Asus\\AppData\\Local\\Google\\Chrome\\User Data\\AkiraProfile")
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    driver.get("https://web.whatsapp.com")

    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
        search_box.click()
        search_box.send_keys(name)
        search_box.send_keys(Keys.ENTER)

        message_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)

        say(f"Message sent to {name}.")
    except Exception as e:
        say("Failed to send the message.")
        print("Error:", e)
    finally:
        time.sleep(2)
        driver.quit()

def extract_message_info(query):
    if "message" in query and "saying" in query:
        try:
            name = query.split("message")[1].split("saying")[0].strip()
            message = query.split("saying")[1].strip()
            return name, message
        except IndexError:
            return None, None
    return None, None

def focus_youtube_tab():
    try:
        windows = gw.getWindowsWithTitle("YouTube")
        for window in windows:
            title = window.title.lower()
            # Ensure it's not just "YouTube" or "search"
            if "youtube" in title and (" - youtube" in title and "watch" in title or "|" in title):
                print(f"Found YouTube video window: {title}")
                pyautogui.moveTo(960, 540)  # Focus center of the screen
                pyautogui.click()
                time.sleep(1)
                return True
        say("YouTube video is not currently playing or window not found.")
    except Exception as e:
        print("Error focusing YouTube window:", e)
    return False





def play_youtube_video(video_name):
    from urllib.parse import quote
    from selenium.webdriver.common.action_chains import ActionChains

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(r"user-data-dir=C:\\Users\\Asus\\AppData\\Local\\Google\\Chrome\\User Data\\AkiraProfile")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        search_query = quote(video_name)
        driver.get(f"https://www.youtube.com/results?search_query={search_query}")
        time.sleep(2)

        # Collect all clickable video elements with href
        video_elements = driver.find_elements(By.ID, "video-title")
        video_url = None

        for video in video_elements:
            try:
                url = video.get_attribute("href")
                if url and "/watch" in url:
                    video_url = url
                    break  # Stop at the first real video link
            except:
                continue

        driver.quit()

        if video_url:
            webbrowser.open(video_url)
            say(f"Playing {video_name} on YouTube.")
        else:
            say("Couldn't find a valid video link.")
            print("No usable video found in results.")

    except Exception as e:
        say("Failed to open video.")
        print("Error:", e)
        driver.quit()



def take_screenshot():
    try:
        # Get current timestamp
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create data/screenshots folder if it doesn't exist
        screenshot_dir = os.path.join("data", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        # Define screenshot file path
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{now}.png")

        # Capture and save screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        say("Screenshot taken and saved.")
    except Exception as e:
        say("Failed to take screenshot.")
        print("Screenshot error:", e)
alarm_ringing = False

def set_alarm(alarm_time_str):
    global alarm_ringing

    try:
        alarm_time_str = alarm_time_str.replace(".", "").replace("  ", " ").strip().lower()
        time_formats = ["%I:%M %p", "%I %M %p", "%I %p", "%I:%M%p", "%I%M%p"]
        alarm_time = None
        for fmt in time_formats:
            try:
                alarm_time = datetime.strptime(alarm_time_str.upper(), fmt)
                break
            except ValueError:
                continue

        if alarm_time is None:
            say("Sorry, I couldn't understand the alarm time format.")
            return

        now = datetime.now()
        alarm_time = now.replace(hour=alarm_time.hour, minute=alarm_time.minute, second=0, microsecond=0)
        if alarm_time < now:
            alarm_time += datetime.timedelta(days=1)

        def alarm_thread():
            global alarm_ringing
            say(f"Alarm set for {alarm_time.strftime('%I:%M %p')}")
            while True:
                if datetime.now() >= alarm_time:
                    alarm_ringing = True
                    # say("Wake up! It's time!")
                    try:
                        while alarm_ringing:
                            playsound("alarm.mp3")
                    except Exception as e:
                        print("Error playing alarm sound:", e)
                    break
                time.sleep(5)

        threading.Thread(target=alarm_thread).start()

    except Exception as e:
        print("Alarm parsing error:", e)
        say("Something went wrong setting the alarm.")

def pause_video():
    if focus_youtube_tab():
        say("Pausing video.")
        pyautogui.press('k')
    else:
        say("No YouTube video is currently playing.")

def play_video():
    if focus_youtube_tab():
        say("Resuming video.")
        pyautogui.press('k')
    else:
        say("No YouTube video is currently playing.")

def next_video():
    if focus_youtube_tab():
        say("Skipping to next video.")
        pyautogui.hotkey('shift', 'n')
    else:
        say("Can't skip. No YouTube video playing.")

def previous_video():
    if focus_youtube_tab():
        say("Going to previous video.")
        pyautogui.hotkey('shift', 'p')
    else:
        say("Can't go to previous. No YouTube video playing.")

def close_youtube():
    try:
        windows = gw.getWindowsWithTitle("")
        for window in windows:
            title = window.title.lower()
            if "youtube" in title and "chrome" in title:
                window.close()
                say("YouTube window closed.")
                return
        say("No YouTube window is currently open.")
    except Exception as e:
        print("Error closing YouTube:", e)
        say("Something went wrong trying to close YouTube.")


def add_reminder(query):
    now = datetime.now()
    reminder_time = None
    message = ""

    if "remind me at" in query:
        match = re.search(r"remind me at (.+?) to (.+)", query)
        if match:
            time_part = match.group(1).strip()
            message = match.group(2).strip()
            reminder_time = parse_absolute_time(time_part)
            if not reminder_time:
                say("I couldn't understand the time format.")
                return

    elif "remind me in" in query:
        match = re.search(r"remind me in (\d+)\s*(minutes?|hours?)\s*to\s*(.+)", query)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            message = match.group(3).strip()
            if "hour" in unit:
                reminder_time = now + timedelta(hours=amount)
            else:
                reminder_time = now + timedelta(minutes=amount)

    elif "remind me to" in query:
        match = re.search(r"remind me to (.+)", query)
        if match:
            message = match.group(1).strip()
            save_context({"reminder_message": message})
            say(f"Sure! When should I remind you to {message}?")
            return

    if reminder_time:
        reminder_data = {
            "time": reminder_time.isoformat(),
            "message": message
        }
        with open(REMINDER_FILE, "r+") as f:
            reminders = json.load(f)
            reminders.append(reminder_data)
            f.seek(0)
            json.dump(reminders, f, indent=4)
        say(f"Reminder set for {reminder_time.strftime('%I:%M %p')} to {message}")
        clear_context()



def reminder_checker():
    while True:
        try:
            with open(REMINDER_FILE, "r") as f:
                reminders = json.load(f)

            if not reminders:
                time.sleep(10)
                continue

            reminders.sort(key=lambda x: x["time"])
            next_reminder = reminders[0]
            reminder_time = datetime.fromisoformat(next_reminder["time"])
            now = datetime.now()

            wait_time = (reminder_time - now).total_seconds()
            if wait_time > 0:
                time.sleep(min(wait_time, 60))  # Wake up early if needed
            else:
                say(f"Reminder: {next_reminder['message']}")
                reminders.pop(0)
                with open(REMINDER_FILE, "w") as f:
                    json.dump(reminders, f, indent=4)
        except Exception as e:
            print("Reminder checker error:", e)
            time.sleep(10)

def parse_absolute_time(time_str):
    import re

    # Normalize the time string
    time_str = time_str.lower()
    time_str = re.sub(r'\.', '', time_str)  # remove periods
    time_str = time_str.replace("am", "AM").replace("pm", "PM")

    # Remove extra spaces
    time_str = ' '.join(time_str.split())

    time_formats = ["%I:%M %p", "%I %M %p", "%I %p", "%I:%M%p", "%I%M%p"]

    for fmt in time_formats:
        try:
            now = datetime.now()
            parsed_time = datetime.strptime(time_str, fmt)
            reminder_time = now.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0, microsecond=0)
            if reminder_time < now:
                reminder_time += timedelta(days=1)
            return reminder_time
        except ValueError:
            continue
    return None

CONTEXT_FILE = "context.json"

def save_context(context_data):
    with open(CONTEXT_FILE, "w") as f:
        json.dump(context_data, f)

def load_context():
    if not os.path.exists(CONTEXT_FILE):
        return None
    with open(CONTEXT_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def clear_context():
    if os.path.exists(CONTEXT_FILE):
        os.remove(CONTEXT_FILE)


def clean_temp_files():
    temp_path = os.environ.get("TEMP") or "C:\\Windows\\Temp"
    try:
        for root, dirs, files in os.walk(temp_path):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    continue
            for dir in dirs:
                try:
                    shutil.rmtree(os.path.join(root, dir), ignore_errors=True)
                except Exception:
                    continue
        say("Temporary files cleaned.")
    except Exception as e:
        say("Failed to clean temp files.")
        print(e)

def empty_recycle_bin():
    try:
        # SHEmptyRecycleBinW params: (None, None, 0x00000001)
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001)
        say("Recycle Bin emptied.")
    except Exception as e:
        say("Failed to empty Recycle Bin.")
        print(e)

def close_background_apps():
    closed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in ['notepad.exe', 'wordpad.exe']:  # You can expand this list
                proc.kill()
                closed += 1
        except Exception:
            continue
    say(f"Closed {closed} background apps.")

def clean_pc():
    say("Starting PC cleanup.")
    clean_temp_files()
    empty_recycle_bin()
    close_background_apps()
    say("PC cleanup completed.")

CONTEXT_FILE = "context.json"

# Ensure context.json exists
def ensure_context_file():
    if not os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "w") as f:
            json.dump({}, f)

ensure_context_file()

def save_context(context_data):
    with open(CONTEXT_FILE, "w") as f:
        json.dump(context_data, f, indent=4)

def load_context():
    with open(CONTEXT_FILE, "r") as f:
        return json.load(f)

def clear_context():
    with open(CONTEXT_FILE, "w") as f:
        json.dump({}, f)

def open_chrome():
    say("Opening Google Chrome.")
    try:
        chrome_path = "C://Program Files//Google//Chrome//Application//chrome.exe"
        if os.path.exists(chrome_path):
            os.startfile(chrome_path)
        else:
            webbrowser.open("https://www.google.com")  # Fallback to default browser
    except Exception as e:
        say("Sorry, I couldn't open Chrome.")
        print("Error:", e)

def control_system(command):
    system_platform = platform.system().lower()

    if "shut down" in command or "shutdown" in command:
        say("Shutting down the system.")
        if system_platform == "windows":
            os.system("shutdown /s /t 1")
        elif system_platform == "linux" or system_platform == "darwin":
            os.system("shutdown now")

    elif "restart" in command:
        say("Restarting the system.")
        if system_platform == "windows":
            os.system("shutdown /r /t 1")
        elif system_platform == "linux" or system_platform == "darwin":
            os.system("reboot")

    elif "log out" in command or "logout" in command:
        say("Logging out.")
        if system_platform == "windows":
            os.system("shutdown -l")
        elif system_platform == "linux":
            os.system("gnome-session-quit --logout --no-prompt")

    elif "lock" in command:
        say("Locking the computer.")
        if system_platform == "windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif system_platform == "linux":
            os.system("gnome-screensaver-command -l")

def sanitize_filename(name):
    """Remove characters not allowed in file names."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def take_note_from_text(note_text):
    notes_dir = "data/notes"
    os.makedirs(notes_dir, exist_ok=True)  # Create folder if not exist

    # Get the first 3-4 words for the filename
    words = note_text.strip().split()
    preview = " ".join(words[:4]) if len(words) >= 4 else " ".join(words)
    preview = sanitize_filename(preview)  # Clean up for filename usage

    filename = os.path.join(notes_dir, f"{preview}.txt")

    # Add timestamp at the top of the note content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note_content_with_timestamp = f"Time and Date: {timestamp}\n\n{note_text}"

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(note_content_with_timestamp)
        say("Got it. I've saved your note.")
    except Exception as e:
        say(f"Failed to save the note: {e}")

def handle_note_feature(query):
    if query.strip().lower().startswith("note "):  # e.g., "note I have a meeting"
        note_content = query.partition("note")[2].strip()
        if note_content:
            take_note_from_text(note_content)
        else:
            say("I heard 'note' but there was nothing to write.")
    elif "take note" in query.lower():
        say("Sure, what would you like me to note down?")
        note_content = takecommand()  # <-- updated here
        if note_content:
            take_note_from_text(note_content)
        else:
            say("There was nothing to note.")


def google_search(query, say=None):
    if not query:
        if say:
            say("What would you like to search for?")
        return
    
    search_query = quote_plus(query)
    url = f"https://www.google.com/search?q={search_query}"
    webbrowser.open(url)

    if say:
        say(f"Searching Google for {query}.")



def search_chatgpt(query, say):
    if query:
        say(f"Searching ChatGPT for {query}")
        webbrowser.open(f"https://chat.openai.com/?q={query.replace(' ', '+')}")
    else:
        say("What should I search on ChatGPT?")


def contains_chatgpt_variant(text):
    variants = [
        "chatgpt", "chat GPT", "chat gpt", "chat g p t", "chat gbt", "xhatgpt", "chatgeeptee",
        "chad gpt", "chattgpt", "chatpt", "chatt", "chagpt"
    ]
    return any(variant in text.lower() for variant in variants)

def take_selfie():
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            say("Sorry, I can't access the camera.")
            return

        say("Get ready, taking a selfie in 3 seconds.")
        cv2.waitKey(3000)  # wait 3 seconds

        ret, frame = cap.read()
        if ret:
            # Create data/selfies folder if it doesn't exist
            folder = os.path.join("data", "selfies")
            os.makedirs(folder, exist_ok=True)

            filename = datetime.now().strftime("selfie_%Y-%m-%d_%H-%M-%S.jpg")
            path = os.path.join(folder, filename)
            cv2.imwrite(path, frame)
            say("Selfie taken and saved.")
        else:
            say("Failed to take selfie.")

        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        say("An error occurred while taking selfie.")
        print("Selfie error:", e)
recording = False
video_writer = None
cap = None

# Ensure the videos directory exists
videos_folder = os.path.join("data", "videos")
if not os.path.exists(videos_folder):
    os.makedirs(videos_folder)

def start_video_recording(filename="recorded_video.avi"):
    global recording, video_writer, cap

    if recording:
        say("Video is already recording.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        say("Failed to access the camera.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 20.0
    width = int(cap.get(3))
    height = int(cap.get(4))

    # Save the video in the 'videos' folder inside the 'data' folder
    filename = os.path.join(videos_folder, filename)

    video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    recording = True
    say("Video recording started.")

    def record():
        while recording:
            ret, frame = cap.read()
            if ret:
                video_writer.write(frame)
            time.sleep(0.05)

    threading.Thread(target=record).start()

def stop_video_recording():
    global recording, video_writer, cap

    if not recording:
        say("Video is not currently recording.")
        return

    recording = False
    time.sleep(0.5)  # Allow last frame to finish

    video_writer.release()
    cap.release()
    cv2.destroyAllWindows()
    say("Video recording stopped and saved.")



screen_recording = False
screen_writer = None
screen_recording_thread = None

def start_screen_recording():
    global screen_recording, screen_writer, screen_recording_thread

    if screen_recording:
        say("Screen recording is already in progress.")
        return

    say("Starting screen recording.")
    screen_recording = True

    def record_screen():
        global screen_writer

        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")

        folder = os.path.join("data", "screen_recordings")
        os.makedirs(folder, exist_ok=True)

        filename = datetime.now().strftime("screen_%Y-%m-%d_%H-%M-%S.avi")
        path = os.path.join(folder, filename)

        screen_writer = cv2.VideoWriter(path, fourcc, 10.0, screen_size)

        while screen_recording:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            screen_writer.write(frame)

        screen_writer.release()
        say("Screen recording stopped and saved.")

    screen_recording_thread = threading.Thread(target=record_screen)
    screen_recording_thread.start()

def stop_screen_recording():
    global screen_recording

    if screen_recording:
        screen_recording = False
    else:
        say("Screen recording is not currently running.")


def add_todo(task):
    os.makedirs("data", exist_ok=True)
    todos_path = os.path.join("data", "todos.json")

    if os.path.exists(todos_path):
        with open(todos_path, "r") as f:
            todos = json.load(f)
    else:
        todos = []

    todos.append({
        "task": task,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(todos_path, "w") as f:
        json.dump(todos, f, indent=4)

    say(f"Added task: {task}")


def add_todo(task):
    os.makedirs("data", exist_ok=True)
    todos_path = os.path.join("data", "todos.json")

    if os.path.exists(todos_path):
        with open(todos_path, "r") as f:
            todos = json.load(f)
    else:
        todos = []

    todos.append({
        "task": task,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(todos_path, "w") as f:
        json.dump(todos, f, indent=4)

    say(f"Added task: {task}")


def list_todos():
    todos_path = os.path.join("data", "todos.json")
    if not os.path.exists(todos_path):
        say("You have no tasks in your to-do list.")
        return

    with open(todos_path, "r") as f:
        todos = json.load(f)

    if not todos:
        say("You have no tasks in your to-do list.")
    else:
        say("Here are your current tasks:")
        for idx, item in enumerate(todos, 1):
            say(f"{idx}. {item['task']}")


def remove_todo(index):
    todos_path = os.path.join("data", "todos.json")
    if not os.path.exists(todos_path):
        say("There are no tasks to remove.")
        return

    with open(todos_path, "r") as f:
        todos = json.load(f)

    if index < 1 or index > len(todos):
        say("Invalid task number.")
        return

    removed_task = todos.pop(index - 1)

    with open(todos_path, "w") as f:
        json.dump(todos, f, indent=4)

    say(f"Removed task: {removed_task['task']}")


# def register_face(name=None):
#     if not name:
#         say("What name should I register this face as?")
#         # name = listen().strip().title()  # Clean and format name input

#     folder_path = os.path.join("data", "known_faces", name)
#     os.makedirs(folder_path, exist_ok=True)

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         say("Camera not accessible.")
#         return

#     say(f"Please look at the camera, {name}. Capturing your face...")
#     ret, frame = cap.read()
#     cap.release()

#     if not ret:
#         say("Failed to capture your face.")
#         return

#     filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
#     file_path = os.path.join(folder_path, filename)
#     cv2.imwrite(file_path, frame)

#     say(f"Face registered successfully under the name {name}.")
# known_encodings = []
# known_names = []




# def say(text):
#     print(f"Akira: {text}")  # Replace with your TTS engine (e.g., pyttsx3 or gTTS)

# def recognize_face_and_act():
#     say("Scanning your face...")
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         say("Camera not accessible.")
#         return

#     ret, frame = cap.read()
#     cap.release()

#     if not ret:
#         say("Failed to capture frame.")
#         return

#     # Convert BGR (OpenCV default) to RGB (face_recognition expects RGB)
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Detect face locations
#     face_locations = face_recognition.face_locations(rgb_frame)

#     if not face_locations:
#         say("No face detected.")
#         return

#     # Encode detected faces
#     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#     for encoding in face_encodings:
#         # Compare with known encodings
#         matches = face_recognition.compare_faces(known_encodings, encoding)
#         face_distances = face_recognition.face_distance(known_encodings, encoding)

#         if len(face_distances) == 0:
#             continue  # No known faces to compare with

#         best_match_index = np.argmin(face_distances)

#         if matches[best_match_index]:
#             name = known_names[best_match_index]
#             say(f"Access granted. Hello {name}.")
#             return

#     # No match found
#     say("Face not recognized. Taking a selfie and locking screen.")

#     # Save selfie to 'data/selfies'
#     selfies_folder = os.path.join("data", "selfies")
#     os.makedirs(selfies_folder, exist_ok=True)
#     timestamp = datetime.now().strftime("unknown_%Y-%m-%d_%H-%M-%S.jpg")
#     selfie_path = os.path.join(selfies_folder, timestamp)
#     cv2.imwrite(selfie_path, frame)

#     # Lock the screen
#     ctypes.windll.user32.LockWorkStation()
