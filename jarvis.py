import google.generativeai as genai
import subprocess
import speech_recognition as sr
from os import environ
import threading
from tkinter import Tk, Label, Toplevel, Button
from PIL import Image, ImageTk
from datetime import datetime
from time import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Futuristic GUI")
        self.root.geometry("500x600")
        self.create_bg()
        self.current_popup = None

    def create_bg(self):
        self.img = Image.open(BG_PATH)
        self.frames = []
        for frame in range(self.img.n_frames):
            self.img.seek(frame)
            frame_image = ImageTk.PhotoImage(self.img.copy())
            self.frames.append(frame_image)
        self.background_label = Label(self.root, bg="black")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.animate_background(0)

    def animate_background(self, frame_idx):
        frame = self.frames[frame_idx]
        self.background_label.configure(image=frame)
        self.root.after(50, self.animate_background, (frame_idx + 1) % len(self.frames))

    def make_popup(self, text):
        if self.current_popup:
            self.current_popup.destroy()
        
        popup = Toplevel(self.root)
        popup.title("Popup")
        min_width, min_height = 300, 200
        lines = text.split("\n")
        max_line_length = max(len(line) for line in lines)
        extra_width = max_line_length * 6
        extra_height = len(lines) * 20
        popup.geometry(f"{min_width + extra_width}x{min_height + extra_height}")
        popup.configure(bg="#1a1a2e")
        
        label = Label(popup, text=text, fg="white", bg="#1a1a2e", font=("Arial", 12), justify="center")
        label.pack(pady=40)

        close_button = Button(popup, text="Close", command=popup.destroy, bg="#3e4a60", fg="white", font=("Arial", 10))
        close_button.pack()

        self.current_popup = popup

BG_PATH = "assets/bg.gif"
genai.configure(api_key=environ['api_key'])
model = genai.GenerativeModel("gemini-1.5-flash")

def make_readable(seconds):
    formatted_time = datetime.fromtimestamp(seconds).strftime('%B %d, %Y, %H:%M:%S')
    return formatted_time

conversation_history = []

def speak(text):
    print(text)
    subprocess.run(['festival', '--tts'], input=text, text=True)

def listen(app):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        app.make_popup("Listening... Please speak clearly.")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            app.make_popup("Recognizing...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand. Please try again.")
            return ""
        except sr.RequestError as e:
            print(f"API request error: {e}")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected in time. Please try again.")
            return ""

def response(prompt):
    global conversation_history
    conversation_history.append(f"You: {prompt}")
    if len(conversation_history) > 10:
        conversation_history.pop(0)
    conversation = "\n".join(conversation_history)
    print("Generating AI response...")
    response = model.generate_content(conversation)
    conversation_history.append(f"AI: {response.text}")
    return response.text

def listen_and_respond(app):
    while True:
        speech_input = listen(app)
        if speech_input:
            print(f"You said: {speech_input}")
            if speech_input.lower() in ["exit", "quit"]:
                speak("Goodbye!")
                break
            elif "time" in speech_input.lower():
                app.make_popup(make_readable(time()))
                speak(make_readable(time()))
            else:
                try:
                    ai_response = response(speech_input)
                    app.make_popup(f"\nAI Response: {ai_response}\n")
                    speak(ai_response)
                except Exception as e:
                    app.make_popup(f"Error generating response: {e}")
                    speak("I encountered an error. Please try again.")

def main():
    root = Tk()
    app = App(root)
    listen_thread = threading.Thread(target=listen_and_respond, args=(app,))
    listen_thread.daemon = True
    listen_thread.start()
    root.mainloop()

if __name__ == "__main__":
    main()