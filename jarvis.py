import subprocess
import speech_recognition as sr
import datetime

commands = {
    "hello: Greets you:",
    "stop: Stops the assistant:",
    "time: Tells the current time:",
    "search: Performs a Google search:",
    "youtube: Opens YouTube Music:",
    "help: Lists all available commands:"
}

def speak(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

def run_assistant():
    speak("Hello. I am your assistant. How can I help you?")
    while True:
        command = listen().lower()
        print("You said:", command)

        if "hello" in command:
            speak("Hi there!")
        elif "stop" in command:
            speak("Goodbye!")
            break
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%H:%M")
            speak(f"The time is {current_time}.")
        elif "search" in command:
            speak("What do you want me to search?")
            query = listen()
            subprocess.run(["xdg-open", f"https://www.google.com/search?q={query}"])
        elif "youtube" in command:
            subprocess.run(['/opt/YouTube Music/youtube-music'])
        elif "help" in command or "command" in command:
            speak(f"My commands are: {commands}")
        else:
            speak("Sorry, I didn't understand that.")

if __name__ == "__main__":
    run_assistant()