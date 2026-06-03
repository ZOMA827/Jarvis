// كشف الدوال لكي يتعرف عليها بايثون فوراً بدون انتظار تحميل باقي الصفحة
eel.expose(DisplayMessage);
function DisplayMessage(message) {
  $(".siri-message li:first").text(message);
  $(".siri-message").textillate("start");
}

eel.expose(ShowHood);
function ShowHood() {
  $("#Oval").attr("hidden", false);
  $("#SiriWave").attr("hidden", true);
}

eel.expose(senderText);
function senderText(message) {
  var chatBox = document.getElementById("chat-canvas-body");
  if (message.trim() !== "") {
    chatBox.innerHTML += `<div class="row justify-content-end mb-4">
        <div class = "width-size">
        <div class="sender_message">${message}</div>
    </div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

eel.expose(receiverText);
function receiverText(message) {
  var chatBox = document.getElementById("chat-canvas-body");
  if (message.trim() !== "") {
    chatBox.innerHTML += `<div class="row justify-content-start mb-4">
        <div class = "width-size">
        <div class="receiver_message">${message}</div>
        </div>
    </div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

eel.expose(hideLoader);
function hideLoader() {
  $("#Loader").attr("hidden", true);
  $("#FaceAuth").attr("hidden", false);
}

eel.expose(hideFaceAuth);
function hideFaceAuth() {
  $("#FaceAuth").attr("hidden", true);
  $("#FaceAuthSuccess").attr("hidden", false);
}

eel.expose(hideFaceAuthSuccess);
function hideFaceAuthSuccess() {
  $("#FaceAuthSuccess").attr("hidden", true);
  $("#HelloGreet").attr("hidden", false);
}

eel.expose(hideStart);
function hideStart() {
  $("#Start").attr("hidden", true);
  setTimeout(function () {
    $("#Oval").addClass("animate__animated animate__zoomIn");
  }, 1000);
  setTimeout(function () {
    $("#Oval").attr("hidden", false);
  }, 1000);
}
// دالة لعرض الأكواد في اللوحة الجانبية (Blade Panel)
// ═══════════════════════════════════════════════════════════
//  JRAVIST — دالة عرض الأكواد البرمجية الهولوغرامية المحمية
// ═══════════════════════════════════════════════════════════
eel.expose(showCodeInBlade);
function showCodeInBlade(codeText) {
    try {
        console.log("🤖 JRAVIST Core: تم استقبال كود لعرضه:", codeText);

        // تنظيف النص البرمجي لحمايته من التنفيذ الخاطئ داخل المتصفح
        let safeCode = codeText.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

        // 1. محاولة أولى: التحقق مما إذا كانت اللوحة الجانبية جاهزة ومدعومة في الـ HTML
        let codeContentEl = document.getElementById("CodeContent");
        if (codeContentEl && typeof openPanel === "function") {
            codeContentEl.innerText = codeText;
            openPanel("HoloCodePanel");
            console.log("🚀 تم عرض الكود بنجاح داخل اللوحة الجانبية (Blade Panel).");
            return "SUCCESS_BLADE";
        }

        // 2. حل احتياطي ذكي: إذا لم تكن اللوحة جاهزة، نعرض الكود داخل صندوق المحادثة مباشرة بتنسيق هولوغرامي جذاب
        let chatBox = document.getElementById("chat-canvas-body");
        if (chatBox) {
            chatBox.innerHTML += `
                <div class="row justify-content-start mb-4">
                    <div class="width-size">
                        <div class="receiver_message" style="font-family: 'JetBrains Mono', monospace; background: rgba(0,200,255,0.04); border: 1px solid var(--cyan); padding: 14px; border-radius: 4px; max-width: 90%; overflow-x: auto; white-space: pre; color: #00c8ff; box-shadow: 0 0 10px rgba(0,200,255,0.1); direction: ltr; text-align: left;">
${safeCode}
                        </div>
                    </div>
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            console.log("📱 تم عرض الكود بنجاح داخل صندوق المحادثة كحل احتياطي آمن.");
            return "SUCCESS_CHAT";
        }

        return "SUCCESS_NO_DOM"; // إرجاع نص دائمًا لضمان سلامة اتصال مكتبة Eel
    } catch (error) {
        console.error("❌ حدث خطأ داخلي في الجافاسكريبت وتمت معالجته آلياً:", error);
        return "JS_ERROR_CAUGHT"; // حماية السيرفر من السقوط (KeyError)
    }
}
// 1. كشف دالة عقد البحث العائمة لبايثون
eel.expose(createSearchNode);

// 2. كشف دالة تغيير وضع الواجهة (setMode) لبايثون
eel.expose(setMode);

// 3. كشف دالة التنبيهات (showToast) لبايثون
eel.expose(showToast);

// 4. دالة مخصصة للتقرير الاستخباراتي تفتح لوحة التقارير وتضع النص داخل #ReportContent
eel.expose(showIntelligenceReport);
function showIntelligenceReport(title, content) {
  // وضع النص داخل منطقة التقرير التي صممتها أنت
  $("#ReportContent").text(content);
  // فتح لوحة التقارير الجانبية
  openPanel("HoloReportPanel");
}