import subprocess
import speech_recognition as sr
from datetime import datetime
import time
import webbrowser
import random
import yt_dlp

def speak(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def make_readable(seconds):
    return datetime.fromtimestamp(seconds).strftime('%B %d, %Y, %H:%M:%S')

def fetch_playlist_videos(playlist_url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_info:
                return [entry['url'] for entry in playlist_info['entries']]
    except Exception as e:
        speak("I couldn't fetch the playlist.")
        print(f"Error: {e}")
    return []

def play_music_with_celluloid(playlist_url):
    video_urls = fetch_playlist_videos(playlist_url)
    if video_urls:
        random_video = random.choice(video_urls)
        subprocess.Popen(["celluloid", random_video])
    else:
        speak("The playlist seems empty or unavailable.")

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

playlist_url = "https://music.youtube.com/playlist?list=PLZ3RLzVsyLkjbc2J0tvwTXjq0fmXca3a1&si=Y2PPqE9hblH4khCC"

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
                play_music_with_celluloid(playlist_url)
            else:
                print(f"Command '{voice_command}' not recognized.")
                speak("I don't have that command. Please try again.")
        except Exception as e:
            print(f"Error generating response: {e}")
            speak("I encountered an error. Please try again.")