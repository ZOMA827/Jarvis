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
eel.expose(showCodeInBlade);
function showCodeInBlade(codeText) {
  // نضع الكود داخل العنصر المخصص له
  $("#CodeContent").text(codeText);
  // نفتح اللوحة الجانبية كما صممتها أنت
  openPanel("HoloCodePanel");
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