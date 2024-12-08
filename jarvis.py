import google.generativeai as genai
import subprocess
import speech_recognition as sr
from os import environ

genai.configure(api_key=environ['api_key'])
model = genai.GenerativeModel("gemini-1.5-flash")

conversation_history = []

def speak(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening... Please speak clearly.")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
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

while True:
    print("Say something to the AI (say 'exit' or 'quit' to exit):")
    speech_input = listen()
    
    if speech_input:
        print(f"You said: {speech_input}")
        if speech_input.lower() in ["exit", "quit"]:
            speak("Goodbye!")
            break
        
        try:
            response = response(speech_input)
            print(f"\nAI Response: {response}\n")
            speak(response)
        except Exception as e:
            print(f"Error generating response: {e}")
            speak("I encountered an error. Please try again.")