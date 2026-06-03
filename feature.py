# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)
import importlib
import os
import sqlite3
import struct
import subprocess
import time
import webbrowser
from shlex import quote
import google.generativeai as genai
import eel
import pvporcupine
import pyaudio
import pyautogui
import pygame
import pywhatkit as kit
from hugchat import hugchat

from backend.command import speak, takecommand
from backend.config import (ASSISTANT_NAME, AUDIO_START_SOUND_PATH,
                            DATABASE_PATH, HUGCHAT_COOKIE_PATH,
                            OPENWEATHERMAP_API_KEY, PORCUPINE_ACCESS_KEY,
                            PORCUPINE_KEYWORDS, PORCUPINE_SENSITIVITY,
                            WHATSAPP_COUNTRY_CODE, WHATSAPP_MESSAGE_DELAY)
from backend.feedback import StatusIndicator, Timer
from backend.helper import extract_yt_term, remove_words
from backend.nlp.command_parser import parse_command
from weather_fetcher import WeatherFetcher

# -----------------------------
# Database & audio setup
# -----------------------------
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
# إنشاء الجدول إذا لم يكن موجوداً
cursor.execute('''CREATE TABLE IF NOT EXISTS sys_command 
                  (id INTEGER PRIMARY KEY, name TEXT, path TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS web_command 
                  (id INTEGER PRIMARY KEY, name TEXT, url TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys 
                  (id INTEGER PRIMARY KEY, key_value TEXT)''')

conn.commit()
pygame.mixer.init()

# -----------------------------
# Weather fetcher setup
# -----------------------------
_weather_fetcher = None

def get_weather_fetcher():
    """Get or create a WeatherFetcher instance."""
    global _weather_fetcher
    if _weather_fetcher is None and OPENWEATHERMAP_API_KEY:
        try:
            _weather_fetcher = WeatherFetcher(OPENWEATHERMAP_API_KEY)
        except ValueError as e:
            print(f"Failed to initialize weather fetcher: {e}")
            return None
    return _weather_fetcher


# -----------------------------
# Play assistant start sound
# -----------------------------
@eel.expose
def play_assistant_sound():
    sound_file = AUDIO_START_SOUND_PATH
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


# -----------------------------
# Intent handling (Parser Integration)
# -----------------------------
def handle_user_text(user_text):
    """Convert recognized text into intent and trigger action."""
    intent = parse_command(user_text)

    if not intent:
        speak("Sorry, I did not understand that.")
        return

    # Time and Date queries
    if intent == "get_time":
        from datetime import datetime

        now = datetime.now().strftime("%H:%M")
        speak(f"The current time is {now}")

    elif intent == "get_date":
        from datetime import datetime

        today = datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")

    # Opening applications
    elif intent == "open_youtube":
        PlayYoutube(user_text)

    elif intent in ["open_whatsapp", "open_calculator", "open_browser"]:
        openCommand(user_text)

    # Weather
    elif intent == "get_weather":
        speak("Please tell me the city name")
        # Note: Weather fetching requires city name, which should be handled separately

    # Music
    elif intent == "play_music":
        speak("Playing music")
        # Note: Can be extended to integrate with music services

    # News
    elif intent == "get_news":
        speak("Fetching latest news")
        # Note: Can be integrated with news_fetcher module

    # Search
    elif intent == "search_google":
        # Remove common search command words to extract the actual search term
        search_words = ["search", "google", "for", "look", "up", "find", "on", "can", "you", "could", "about", "information"]
        search_term = user_text.lower()
        for word in search_words:
            search_term = search_term.replace(word, "")
        search_term = search_term.strip()
        
        if search_term:
            speak(f"Searching Google for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
        else:
            speak("What would you like me to search for?")

    # Screenshot
    elif intent == "take_screenshot":
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            speak(f"Screenshot saved as {filename}")
        except Exception as e:
            speak("Could not take screenshot")
            print(f"Screenshot error: {e}")

    # System commands
    elif intent == "shutdown":
        speak("Are you sure you want to shutdown? This action cannot be undone.")
        # Note: Actual shutdown requires user confirmation in production
        # Uncomment the following for actual shutdown:
        # confirmation = takecommand()
        # if confirmation and "yes" in confirmation.lower():
        #     speak("Shutting down the system")
        #     if os.name == 'nt':  # Windows
        #         os.system("shutdown /s /t 1")
        #     else:  # Unix/Linux/Mac
        #         os.system("shutdown -h now")

    elif intent == "restart":
        speak("Are you sure you want to restart? This action cannot be undone.")
        # Note: Actual restart requires user confirmation in production
        # Uncomment the following for actual restart:
        # confirmation = takecommand()
        # if confirmation and "yes" in confirmation.lower():
        #     speak("Restarting the system")
        #     if os.name == 'nt':  # Windows
        #         os.system("shutdown /r /t 1")
        #     else:  # Unix/Linux/Mac
        #         os.system("shutdown -r now")

    else:
        speak("Intent recognized but no action defined.")


# -----------------------------
# Core Command Functions
# -----------------------------
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower()

    app_name = query.strip()
    if not app_name:
        return
    # --- أضف هذا الجزء الصغير هنا ---
    if app_name == "youtube":
        StatusIndicator.processing("Opening YouTube")
        speak("Opening YouTube")
        import webbrowser
        webbrowser.open("https://www.youtube.com")
        return
    # --------------------------------

    try:
        with Timer(f"Opening {app_name}"):
            # Try system apps
            cursor.execute("SELECT path FROM sys_command WHERE name IN (?)", (app_name,))
            results = cursor.fetchall()

            if results:
                StatusIndicator.processing(f"Opening {query}")
                speak("Opening " + query)
                os.startfile(results[0][0])
                return

            # Try web URLs
            cursor.execute("SELECT url FROM web_command WHERE name IN (?)", (app_name,))
            results = cursor.fetchall()

            if results:
                StatusIndicator.processing(f"Opening {query}")
                speak("Opening " + query)
                webbrowser.open(results[0][0])
                return

            # --- التحديث الجديد: البحث في اختصارات سطح المكتب ---
            import glob
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcuts = glob.glob(f"{desktop_path}\\*{app_name}*.lnk") + glob.glob(f"{desktop_path}\\*{app_name}*.url")
            
            if shortcuts:
                StatusIndicator.processing(f"Opening {query} from desktop")
                speak(f"Opening {query}")
                os.startfile(shortcuts[0])
                return
            # ----------------------------------------------------

            # Try OS-level open
            StatusIndicator.processing(f"Opening {query}")
            speak("Opening " + query)
            os.system("start " + query)

    except Exception as e:
        StatusIndicator.error(f"Error in openCommand: {e}")
        print("Error in openCommand:", e)
        speak("Something went wrong while opening.")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    
    # حماية من خطأ NoneType إذا لم يتمكن من استخراج الكلمة
    if not search_term:
        # نأخذ الجملة كاملة ونحذف منها الكلمات الزائدة
        search_term = query.lower().replace("open youtube", "").replace("play", "").replace("and", "").strip()
        
    if not search_term:
        speak("What do you want to play on YouTube?")
        return

    # استعملنا str() باش نضمنو عدم حدوث كراش
    StatusIndicator.processing(f"Playing {str(search_term)} on YouTube")
    speak("Playing " + str(search_term) + " on YouTube")
    
    with Timer("YouTube playback"):
        kit.playonyt(str(search_term))


# -----------------------------
# Hotword detection + parser link
# -----------------------------
def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keywords=PORCUPINE_KEYWORDS,
            sensitivities=[PORCUPINE_SENSITIVITY] * len(PORCUPINE_KEYWORDS),
        )
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected!")

                # Simulate shortcut (Win + J)
                pyautogui.keyDown("win")
                pyautogui.press("j")
                time.sleep(2)
                pyautogui.keyUp("win")

                # Capture and process user speech
                recognized_text = takecommand()
                if recognized_text:
                    print("You said:", recognized_text)
                    handle_user_text(recognized_text)

    except Exception as e:
        print("Error in hotword:", e)
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


# -----------------------------
# WhatsApp contact + messaging
# -----------------------------
def findContact(query):
    words_to_remove = [
        ASSISTANT_NAME,
        "make",
        "a",
        "to",
        "phone",
        "call",
        "send",
        "message",
        "wahtsapp",
        "video",
    ]
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        StatusIndicator.processing("Searching for contact")
        cursor.execute(
            "SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
            ("%" + query + "%", query + "%"),
        )
        results = cursor.fetchall()
        if not results:
            StatusIndicator.warning("Contact not found")
            speak("Contact not found.")
            return 0, 0

        mobile_number = str(results[0][0])
        if not mobile_number.startswith(WHATSAPP_COUNTRY_CODE):
            mobile_number = WHATSAPP_COUNTRY_CODE + mobile_number

        StatusIndicator.success("Contact found")
        return mobile_number, query
    except Exception as e:
        StatusIndicator.error(f"Error in findContact: {e}")
        print("Error in findContact:", e)
        speak("Could not find the contact.")
        return 0, 0


def whatsApp(Phone, message, flag, name):
    if flag == "message":
        target_tab = 12
        jarvis_message = "Message sent successfully."
    elif flag == "call":
        target_tab = 7
        message = ""
        jarvis_message = "Calling contact..."
    else:
        target_tab = 6
        message = ""
        jarvis_message = "Starting video call..."

    StatusIndicator.processing("Initiating WhatsApp action")
    
    with Timer(f"WhatsApp {flag}"):
        encoded_message = quote(message)
        whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"
        full_command = f'start "" "{whatsapp_url}"'

        subprocess.run(full_command, shell=True)
        time.sleep(WHATSAPP_MESSAGE_DELAY)
        subprocess.run(full_command, shell=True)

        pyautogui.hotkey("ctrl", "f")
        for _ in range(target_tab - 1):
            pyautogui.hotkey("tab")
        pyautogui.hotkey("enter")

    StatusIndicator.success(jarvis_message)
    speak(jarvis_message)



# -----------------------------
# Chatbot fallback - مع نظام تدوير المفاتيح المركزي
# -----------------------------
def chatBot(query):
    user_input = query.lower()
    StatusIndicator.processing("Querying Gemini AI...")
    
    # جلب المفاتيح من ملف config الموحد
    from backend.config import GEMINI_API_KEYS
    
    with Timer("Gemini AI response"):
        ai_reply = None
        from google.api_core import exceptions
        
        # تجربة المفاتيح بالتوالي حتى يشتغل أحدها
        for index, key in enumerate(GEMINI_API_KEYS):
            try:
                os.environ["GOOGLE_API_KEY"] = key
                genai.configure(api_key=key) 
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # نبعثو السؤال لجمناي
                response = model.generate_content(user_input)
                ai_reply = response.text
                print(f"✅ تم الرد بنجاح باستخدام المفتاح رقم {index + 1}")
                break  # نجحنا، نخرج من الحلقة
            except exceptions.ResourceExhausted:
                print(f"⚠️ انتهى رصيد المفتاح رقم {index + 1}، جاري تجربة المفتاح التالي...")
                continue
            except Exception as e:
                print(f"⚠️ خطأ غير متوقع في المفتاح رقم {index + 1}: {e}")
                continue
        
        # حماية في حال توقفت كل المفاتيح تماماً
        if ai_reply is None:
            ai_reply = "عذراً يا خويا، يبدو أن جميع مفاتيح الـ API استهلكت رصيدها اليومي حالياً."
        else:
            # تنظيف النص
            ai_reply = ai_reply.replace("*", "").replace("#", "")
    
    StatusIndicator.response(ai_reply)
    print(ai_reply)
    speak(ai_reply)
    return ai_reply


# -----------------------------
# Weather functions
# -----------------------------
def get_weather(city_name):
    """
    Fetch and display current weather for a city.
    
    Args:
        city_name (str): Name of the city
    """
    fetcher = get_weather_fetcher()
    if not fetcher:
        StatusIndicator.error("Weather API key is not configured")
        speak("Weather API key is not configured. Please set OPENWEATHERMAP_API_KEY in your environment.")
        return
    
    StatusIndicator.processing(f"Fetching weather for {city_name}...")
    
    with Timer(f"Weather fetch for {city_name}"):
        weather_data, error = fetcher.fetch_current_weather(city_name)
    
    if error:
        StatusIndicator.error(f"Weather error: {error}")
        speak(f"Sorry, I encountered an error: {error}")
        print(f"Weather error: {error}")
    elif weather_data:
        response = (
            f"Weather in {weather_data['city']}, {weather_data['country']}. "
            f"Temperature is {weather_data['temperature']} degrees Celsius, "
            f"feels like {weather_data['feels_like']} degrees. "
            f"Condition: {weather_data['condition']}. "
            f"Humidity is {weather_data['humidity']} percent."
        )
        StatusIndicator.success(f"Weather data retrieved for {city_name}")
        StatusIndicator.info(fetcher.format_current_weather(weather_data))
        speak(response)
        print(fetcher.format_current_weather(weather_data))


def get_weather_forecast(city_name, days=5):
    """
    Fetch and display weather forecast for a city.
    
    Args:
        city_name (str): Name of the city
        days (int): Number of days (3-5)
    """
    fetcher = get_weather_fetcher()
    if not fetcher:
        StatusIndicator.error("Weather API key is not configured")
        speak("Weather API key is not configured. Please set OPENWEATHERMAP_API_KEY in your environment.")
        return
    
    StatusIndicator.processing(f"Fetching {days}-day forecast for {city_name}...")
    
    with Timer(f"Weather forecast for {city_name}"):
        forecast_data, error = fetcher.fetch_forecast(city_name, days)
    
    if error:
        StatusIndicator.error(f"Forecast error: {error}")
        speak(f"Sorry, I encountered an error: {error}")
        print(f"Forecast error: {error}")
    elif forecast_data:
        StatusIndicator.success(f"Forecast data retrieved for {city_name}")
        speak(f"Here is the {days} day forecast for {city_name}")
        StatusIndicator.info(fetcher.format_forecast(forecast_data))
        print(fetcher.format_forecast(forecast_data))
        
        # Provide a brief summary via speech
        first_day = forecast_data[0]
        last_day = forecast_data[-1]
        summary = (
            f"On the first day of the forecast: {first_day['temp_min']} to {first_day['temp_max']} degrees, {first_day['condition']}. "
            f"Later in the forecast: {last_day['temp_min']} to {last_day['temp_max']} degrees, {last_day['condition']}."
        )
        speak(summary)
