import os
import eel
from backend.command import speak, takeAllCommands

def start():
    # 1. إعداد مجلد الواجهة الرسومية
    eel.init("frontend")
    
    print("ℹ Initializing Jarvis AI Assistant...")
    
    # 2. تشغيل السيرفر وفتح المتصفح (يجب أن يكون هنا أولاً!)
    print("⚙️ Opening web interface...")
    eel.start("index.html", mode="chrome", block=False, port=8000)
    print("✓ Web interface available at http://localhost:8000")
    
    # إعطاء المتصفح ثانيتين ليقوم بتحميل الجافاسكربت (controller.js) والاتصال بالبايثون
    eel.sleep(2.0)
    
    # 3. الآن يمكن للمساعد التحدث وتغيير النصوص في الواجهة بدون أخطاء
    speak("Initializing Jarvis. System is online.")
    
    # 4. الحلقة المستمرة لربط الصوت بـ Gemini
    print("✓ Jarvis is now running and listening for your voice...")
    while True:
        try:
            takeAllCommands()
        except Exception as e:
            print(f"Error in loop: {e}")
            
        eel.sleep(1)

if __name__ == "__main__":
    start()