import google.generativeai as genai
import subprocess
import speech_recognition as sr
from os import environ

genai.configure(api_key=environ['api_key'])
model = genai.GenerativeModel("gemini-1.5-flash")

def speak(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def listen_to_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("listening...")
        audio = recognizer.listen(source)
        try:
            print("recognizing...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"could not request results from Google AI api; {e}")
            return ""

while True:
    print("Say something to the AI:")
    speech_input = listen_to_speech()
    
    if speech_input:
        print(f"You said: {speech_input}")

        if speech_input.lower() in ["exit", "quit"]:
            speak("Goodbye!")
            break

        response = model.generate_content(speech_input)
        
        print(f"\n\n{response.text}\n\n")
        speak(response.text)