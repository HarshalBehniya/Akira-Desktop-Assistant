import tkinter as tk
from tkinter import scrolledtext
import threading
from akira_engine import *
from PIL import Image, ImageTk  
from pystray import Icon, MenuItem, Menu


class AkiraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Akira Desktop Assistant")
        self.root.geometry("800x600")  # Updated dimensions for better UI
        self.root.configure(bg="#2e2e2e")
        self.root.minsize(700, 500)  # Minimum size for responsiveness

        # Set the icon for the window (Ensure you have an .ico file in the same directory or specify the path)
        self.root.iconbitmap('akira_icon.ico')  # Replace 'akira_icon.ico' with your icon filename

        
        # Header Label with sleek design
        self.header = tk.Label(
            root,
            text="AKIRA DESKTOP ASSISTANT",
            font=("Segoe UI", 22, "bold"),
            fg="#007acc",
            bg="#2e2e2e"
        )
        self.header.pack(pady=(20, 10))

        # Output Box for conversation, includes padding and margin
        self.output_box = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=90,
            height=20,
            font=("Consolas", 11),
            fg="white",
            bg="#1e1e1e",
            insertbackground="white",
            bd=0,
            highlightthickness=0,
            padx=15,
            pady=15
        )
        self.output_box.pack(padx=20, pady=(10, 15))

        # Entry frame containing text input and send button, includes smooth styling
        self.entry_frame = tk.Frame(
            root,
            bg="#2e2e2e",
            pady=10
        )
        self.entry_frame.pack(pady=15, padx=20, fill=tk.X)

        self.entry = tk.Entry(
            self.entry_frame,
            font=("Consolas", 14),
            fg="white",
            bg="#444444",
            insertbackground="white",
            bd=0,
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.send_query())

        self.send_button = tk.Button(
            self.entry_frame,
            text="Send",
            font=("Segoe UI", 12),
            command=self.send_query,
            bg="#007acc",
            fg="white",
            activebackground="#005f99",
            relief=tk.RAISED,
            bd=3,
            padx=10,
            pady=5
        )
        self.send_button.pack(side=tk.RIGHT, padx=10)

        # Toggle voice/text mode with custom styling
        self.voice_mode = True
        self.active = False
        self.retry_count = 0

         # Adding Notes Button
        self.notes_button = tk.Button(self.root, text="Open Notes", font=("Segoe UI", 12), command=self.open_notes, bg="#4CAF50", fg="white", activebackground="#45a049", relief=tk.FLAT)
        self.notes_button.pack(pady=10)


        threading.Thread(target=reminder_checker, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

        # Create a status bar for better user feedback
        self.status_bar = tk.Label(
            root,
            text="Akira is ready...",
            font=("Segoe UI", 10),
            fg="white",
            bg="#2e2e2e",
            anchor="w",
            padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def update_status(self, status_text):
        self.status_bar.config(text=status_text)

    def send_query(self):
        query = self.entry.get()
        self.entry.delete(0, tk.END)
        if query:
            self.handle_query(query)

    def listen_loop(self):
        while True:
            if self.voice_mode:
                query = takecommand()
                if query:
                    self.root.after(0, lambda q=query: self.handle_query(q))

    def open_notes(self):
        # Create a new window to display notes
        notes_window = tk.Toplevel(self.root)
        notes_window.title("Your Notes")
        notes_window.geometry("600x400")

        notes_text = scrolledtext.ScrolledText(notes_window, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10), fg="white", bg="#2b2b2b", insertbackground="white")
        notes_text.pack(padx=20, pady=20)

        # Load all notes from the 'data/notes' folder
        notes_folder = 'data/notes'
        if not os.path.exists(notes_folder):
            os.makedirs(notes_folder)

        notes = []
        for note_filename in os.listdir(notes_folder):
            if note_filename.endswith(".txt"):
                with open(os.path.join(notes_folder, note_filename), 'r') as note_file:
                    notes.append(note_file.read())
        
        if notes:
            notes_text.insert(tk.END, "\n\n".join(notes))
        else:
            notes_text.insert(tk.END, "No notes available.")
        
    def handle_query(self, query):
        self.log("You: " + query)


        context = load_context()
        # recognize_face_and_act()
        if context and "reminder_message" in context:
            if "in" in query or "at" in query:
                full_reminder_query = f"remind me {query} to {context['reminder_message']}"
                clear_context()
                self.retry_count = 0
                add_reminder(full_reminder_query)
            else:
                self.retry_count += 1
                if self.retry_count >= 2:
                    say("I couldn't understand the time. Let's try again later.")
                    clear_context()
                    self.retry_count = 0
                else:
                    say("When should I remind you?")
            return

        if "remind me to" in query and ("at" not in query and "in" not in query):
            match = re.search(r"remind me to (.+)", query)
            if match:
                reminder_msg = match.group(1).strip()
                say(f"Sure! When should I remind you to {reminder_msg}?")
                save_context({"reminder_message": reminder_msg})
            else:
                say("What should I remind you about?")
            return

        if "remind me" in query and ("at" in query or "in" in query):
            add_reminder(query)
            return

        if "akira" in query and not self.active:
            say("Yes Harshal")
            self.active = True
            return

        if self.active:
            global alarm_ringing

            if alarm_ringing and "stop alarm" in query:
                say("Stopping the alarm.")
                alarm_ringing = False
                return

            if "stop" in query:
                say("Stopping Akira...")
                self.active = False
                return

            if "switch to text mode" in query:
                global input_mode
                input_mode = "text"
                say("Switched to text mode. You can now type your commands.")
                return

            if "switch to voice mode" in query:
                input_mode = "voice"
                say("Switched to voice mode. You can now speak your commands.")
                return

            sites = [
                ("youtube", "https://www.youtube.com"),
                ("google", "https://www.google.com"),
                ("gmail", "https://mail.google.com"),
                ("chat gpt", "https://www.openai.com/chatgpt")
            ]
            for name, url in sites:
                if f"open {name}" in query:
                    say(f"Opening {name}")
                    webbrowser.open(url)
                    return

            if "play" in query and "on youtube" in query:
                video_name = query.replace("play", "").replace("on youtube", "").strip()
                play_youtube_video(video_name)
                return

            if "take a screenshot" in query or "screenshot" in query:
                take_screenshot()
                return

            if "set alarm for" in query:
                match = re.search(r"set alarm for (.+)", query)
                if match:
                    set_alarm(match.group(1).strip())
                    return

            if "pause video" in query:
                pause_video()
                return

            if "resume video" in query or "play video" in query:
                play_video()
                return

            if "next video" in query:
                next_video()
                return

            if "previous video" in query:
                previous_video()
                return

            if "close youtube" in query:
                close_youtube()
                return

            if "remind me" in query:
                add_reminder(query)
                return

            if "clean my pc" in query or "cleanup" in query:
                clean_pc()
                return

            if "open chrome" in query:
                open_chrome()
                return

            if any(x in query for x in ["shut down", "restart", "log out", "lock"]):
                control_system(query)
                return

            if "note" in query or "take note" in query:
                handle_note_feature(query)
                return

            if any(x in query for x in ["search google", "look up", "google"]):
                if "google" in query:
                    search_term = query.split("google", 1)[1].strip()
                    return
                elif "search google for" in query:
                    search_term = query.split("search google for", 1)[1].strip()
                    return
                elif "look up the" in query:
                    search_term = query.split("look up the", 1)[1].strip()
                    return
                elif "look up" in query:
                    search_term = query.split("look up", 1)[1].strip()
                    return
                else:
                    search_term = ""
                google_search(search_term, say)
                return

            if contains_chatgpt_variant(query) and ("search" in query or "ask" in query):
                query_clean = query.lower()
                for word in ["search", "ask", "chatgpt", "chat gpt", "chat g p t", "chat gbt", "xhatgpt", "chad gpt", "chatgeeptee", "chattgpt", "chatpt"]:
                    query_clean = query_clean.replace(word, "")
                search_chatgpt(query_clean.strip(), say)
                return

            if "take selfie" in query or "click my photo" in query:
                take_selfie()
                return

            if any(x in query for x in ["take video", "start video", "start recording"]):
                start_video_recording()
                return

            if any(x in query for x in ["end video", "stop video", "end recording", "stop recording"]):
                if recording:
                    stop_video_recording()
                else:
                    say("Video is not currently recording.")
                return

            if "start screen recording" in query or "record screen" in query:
                start_screen_recording()
                return

            if "end screen recording" in query or "stop screen recording" in query:
                stop_screen_recording()
                return

            if "add task" in query or "add to do" in query:
                task = query.replace("add task", "").replace("add to-do", "").strip()
                add_todo(task)
                return

            if any(x in query for x in ["show to do", "show tudu", "list task", "list my tasks", "show my tasks", "show my task", "show task", "show tasks"]):
                list_todos()
                return

            if "remove task" in query or "delete task" in query:
                index_str = ''.join([c for c in query if c.isdigit()])
                if index_str:
                    remove_todo(int(index_str))
                else:
                    say("Please specify the task number to remove.")
                return

            if "register my face" in query:
                if "as" in query:
                    name = query.split("as")[-1].strip().title()
                    register_face(name)
                else:
                    register_face()
                return

            name, message = extract_message_info(query)
            if name and message:
                say(f"Sending message to {name} saying {message}")
                whatsapp_message(name, message)
                return


if __name__ == "__main__":
    root = tk.Tk()
    app = AkiraApp(root)
    root.mainloop()