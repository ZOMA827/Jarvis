import eel
import importlib
import os
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
# ─── تأمين وإنشاء جدول المفاتيح فوراً عند إقلاع البرنامج ──────────────────
import sqlite3
from backend.config import DATABASE_PATH

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys 
                      (id INTEGER PRIMARY KEY, key_value TEXT)''')
    conn.commit()
    conn.close()
    print("✅ تم التأكد من وجود جدول api_keys بنجاح.")
except Exception as e:
    print(f"⚠️ خطأ أثناء التأمين المبكر لقاعدة البيانات: {e}")
# ───────────────────────────────────────────────────────────────────
from backend.config import GEMINI_API_KEYS
from backend.config import (SPEECH_LANGUAGE, SPEECH_PAUSE_THRESHOLD,
                            SPEECH_PHRASE_TIMEOUT, SPEECH_TIMEOUT, TTS_ENGINE,
                            TTS_RATE, TTS_VOICE_ID)
from backend.feedback import StatusIndicator, Timer
from google.api_core import exceptions

# =====================================================================
# إعدادات Gemini API (نظام تدوير المفاتيح التلقائي والأدوات الهولوغرامية)
# =====================================================================


current_key_index = 0
chat = None
model = None

# ── 1. أدوات التحكم في النظام الأساسية ──────────────────────────────
def open_application(app_name: str):
    """Use this tool to open any application, software, or website on the computer."""
    from backend.feature import openCommand
    openCommand(app_name)
    return f"Successfully opened {app_name}"

def play_on_youtube(search_query: str):
    """Use this tool to play any video or music on YouTube based on a search query."""
    from backend.feature import PlayYoutube # تأكد من اسم الدالة في feature
    PlayYoutube(search_query)
    return f"Playing {search_query} on YouTube"

def check_weather(city_name: str):
    """Use this tool to check the current weather for a specific city."""
    from backend.feature import check_weather as run_weather
    run_weather(city_name)
    return f"Checked weather for {city_name}"

def check_weather_forecast(city_name: str, days: int = 3):
    """Use this tool to get the weather forecast for a city for a specific number of days."""
    from backend.feature import check_weather_forecast as run_forecast
    run_forecast(city_name, days)
    return f"Checked {days}-day forecast for {city_name}"

def handle_whatsapp(contact_name: str, message: str):
    """Use this tool to send a WhatsApp message to a specific contact."""
    from backend.feature import handle_whatsapp as run_whatsapp
    run_whatsapp(contact_name, message)
    return f"Sent WhatsApp message to {contact_name}"


# ── 2. الأدوات الهولوغرامية الجديدة المتوافقة مع واجهتك ─────────────────
def show_code_on_screen(code_text: str):
    """
    CRITICAL: Use this tool EVERY TIME the user asks you to write, generate, or fix any programming code 
    (HTML, CSS, JavaScript, Python, etc.). This opens the specialized HoloCodePanel.
    """
    eel.showCodeInBlade(code_text) # استدعاء جافاسكريبت المباشر
    return "The code has been successfully displayed on the holographic code panel."

def create_search_node(title: str, content: str, url: str = "No URL"):
    """
    CRITICAL: Use this tool when the user asks for a quick definition, a fact, or quick search results.
    This creates a beautiful floating node/bubble on the interface containing the summary.
    """
    eel.createSearchNode(title, content, url)
    return f"Search node for '{title}' created successfully."

def change_interface_mode(mode_name: str):
    """
    Use this tool when the user tells you to change the system mode or mood.
    Available modes to pass: 'idle', 'listen', 'think', 'search', 'vision'
    """
    if mode_name in ['idle', 'listen', 'think', 'search', 'vision']:
        eel.setMode(mode_name)
        return f"System interface appearance successfully shifted to '{mode_name}' mode."
    return "Invalid mode name."

def show_system_notification(message: str):
    """
    Use this tool to send brief, urgent alerts or pop-up status updates directly to the user's screen.
    """
    eel.showToast(message)
    return "Notification sent to the UI."

def show_intelligence_report(title: str, report_content: str):
    """
    CRITICAL: Use this tool when the user asks for a comprehensive analysis, a long essay, a full report, 
    or deep information about a topic. This opens the big Intelligence Report panel on the UI.
    """
    eel.showIntelligenceReport(title, report_content)
    return "Intelligence report generated and displayed on the screen."

# في أعلى ملف command.py اجعل القائمة فارغة افتراضياً
GEMINI_API_KEYS = []
current_key_index = 0
chat = None
model = None

# ── 3. دالة تهيئة الجلسة الذكية (قلب النظام) ───────────────────────────
def init_gemini_chat():
    global chat, model, current_key_index, GEMINI_API_KEYS
    import sqlite3
    from backend.config import DATABASE_PATH
    
    # 1. جلب المفاتيح ديناميكياً من قاعدة البيانات وتأمين وجود الجدول
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 🔥 حركة ذكية: إنشـاء الجدول فوراً هنا لو مش موجود لحل مشكلة no such table للأبد
        cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys 
                          (id INTEGER PRIMARY KEY, key_value TEXT)''')
        conn.commit()
        
        cursor.execute("SELECT key_value FROM api_keys")
        rows = cursor.fetchall()
        conn.close()
        GEMINI_API_KEYS = [r[0] for r in rows]
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب المفاتيح من قاعدة البيانات: {e}")
        GEMINI_API_KEYS = []

    # إذا كانت قاعدة البيانات فارغة (أول إقلاع للتطبيق)، نتوقف هنا بسلام دون عمل Crash
    if not GEMINI_API_KEYS:
        print("⚠️ نظام جارفيس بانتظار حقن مفاتيح الـ API من الواجهة الرسومية...")
        return False

    # تهيئة المفتاح الحالي من القائمة المستخرجة
    genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
    
    # تجميع كافة الأدوات ليراها جيميناي ويستخدمها
    all_tools = [
        open_application, 
        play_on_youtube, 
        check_weather, 
        check_weather_forecast, 
        handle_whatsapp,
        show_code_on_screen,        # أداة الأكواد الخاصة بك
        create_search_node,         # أداة عقد البحث
        change_interface_mode,      # أداة تغيير وضع الواجهة
        show_system_notification,   # أداة التنبيهات
        show_intelligence_report    # أداة التقارير
    ]
    
    # الأوامر الصارمة والنظام السيادي لـ جارفيس
    jarvis_instructions = (
        "You are jarvis, an advanced holographic AI operating system core. "
        "CRITICAL RULE 1: Never write programming code (HTML, CSS, JS, Python, etc.) directly in the text chat. "
        "You MUST always use the 'show_code_on_screen' tool to display code on the user's holographic panel. "
        "CRITICAL RULE 2: If the user asks for quick info or search, use 'create_search_node'. "
        "CRITICAL RULE 3: For long essays or complex reports, use 'show_intelligence_report'. "
        "Act as a professional, powerful AI assistant."
    )
    
    # بناء النموذج بالأدوات والتعليمات
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=all_tools,
        system_instruction=jarvis_instructions
    )
    
    # تفعيل ميزة استدعاء الدوال التلقائي
    chat = model.start_chat(enable_automatic_function_calling=True)
    print(f"🤖 jarvis Core initialized with all Holographic Tools using Key #{current_key_index + 1}")
    return True

# =====================================================================
# الوظائف الأساسية للمساعد الصوتي
# =====================================================================

def speak(text):
    text = str(text)
    engine = pyttsx3.init(TTS_ENGINE)
    voices = engine.getProperty("voices")
    
    # حماية: إذا لقاو أصوات مثبتة، نخير الافتراضي أو المتاح بلا ما يصرى خطأ الـ Index
    if voices:
        try:
            # نحاول نستعمل الصوت المكتوب في الإعدادات
            engine.setProperty("voice", voices[TTS_VOICE_ID].id)
        except IndexError:
            # إذا الرقم مش موجود، نستعمل أول صوت متاح في الويندوز تلقائياً
            engine.setProperty("voice", voices[0].id)
            
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()
    engine.setProperty("rate", TTS_RATE)
    eel.receiverText(text)

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        StatusIndicator.listening("I'm listening...")
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = SPEECH_PAUSE_THRESHOLD
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, SPEECH_TIMEOUT, SPEECH_PHRASE_TIMEOUT)

    try:
        StatusIndicator.processing("Recognizing...")
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        
        with Timer("Speech recognition") as recognition_timer:
            query = r.recognize_google(audio, language=SPEECH_LANGUAGE)
        
        StatusIndicator.command(f"User said: {query}")
        print(f"User said: {query}\n")
        eel.DisplayMessage(query)

        speak(query)
    except Exception as e:
        StatusIndicator.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()

@eel.expose
def takeAllCommands(message=None):
    # 1. نقلنا الـ global هنا في السطر الأول تماماً لتفادي الخطأ للابد
    global chat, current_key_index
    
    # 2. الفحص يتم هنا في السطر الثاني مباشرة
    if chat is None:
        return

    try:
        # 3. جلب النص بأمان
        if message:
            query = message.lower()
        else:
            raw_query = takecommand()
            # إذا المايك لم يسمع شيئاً (أرجع None)، نوقف الدالة بصمت بدون أخطاء
            if raw_query is None:
                return 
            query = raw_query.lower()

        # 4. بوابة التفتيش الذكية: لحماية الرصيد
        if query == "none" or query.strip() == "":
            return 
        
        # 5. إذا كان هناك كلام حقيقي، نقوم بمعالجته وإرساله
        print(f"User said: {query}")
        eel.senderText(query)
        
        response = None
        
        # محاولة الإرسال مع التبديل التلقائي عند الخطأ
        for _ in range(len(GEMINI_API_KEYS)):
            try:
                response = chat.send_message(query)
                break 
            except Exception as e:
                print(f"❌ فشل المفتاح الحالي: {e}")
                current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
                print(f"🔄 جاري المحاولة باستخدام المفتاح رقم {current_key_index + 1}")
                init_gemini_chat() # إعادة تهيئة الجلسة بالمفتاح الجديد
        
        if response is None:
            raise Exception("جميع المفاتيح المتاحة استهلكت رصيدها اليومي!")

        # تنظيف النص من علامات التنسيق
        ai_reply = response.text.replace("*", "").replace("#", "")
        
        print(f"Gemini says: {ai_reply}")
        speak(ai_reply)
        eel.receiverText(ai_reply) # إرسال الرد ليعرض في الواجهة الرسومية أيضاً

    except Exception as e:
        StatusIndicator.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        speak("Sorry, I encountered an issue connecting to my core systems.")

    eel.ShowHood()
    # ربط الاسم القديم بالجديد باش main.py ما يديرش خطأ
take_command = takecommand


@eel.expose
def check_api_keys_exist():
    """تحقق هل توجد مفاتيح مسجلة أم لا"""
    import sqlite3
    from backend.config import DATABASE_PATH
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM api_keys")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        return False

@eel.expose
def save_user_keys(keys_list):
    """تحفظ المفاتيح القادمة من الواجهة الرسومية وتقوم بتشغيل جارفيس فوراً"""
    import sqlite3
    from backend.config import DATABASE_PATH
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_keys")
        for key in keys_list:
            if key.strip():
                cursor.execute("INSERT INTO api_keys (key_value) VALUES (?)", (key.strip(),))
        conn.commit()
        conn.close()
        
        # 🔥 بعد الحفظ بنجاح، نقوم بتهيئة الذكاء الاصطناعي فوراً ليعمل التطبيق دون إعادة تشغيل!
        return init_gemini_chat()
    except Exception as e:
        print(f"Error saving keys: {e}")
        return False