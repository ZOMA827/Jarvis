/* ═══════════════════════════════════════════════════════════
   JRAVIST — main.js
   All eel bindings preserved from original.
   New: Holographic search node system, orb state management,
        blade panels, draggable nodes, mode switching.
   ═══════════════════════════════════════════════════════════ */
$(document).ready(function () {

  /* ── Init Eel ─────────────────────────────────── */
  eel.init()();

  /* ── Textillate setup ──────────────────────────── */
  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in:  { effect: "fadeInUp", sync: true },
    out: { effect: "fadeOutUp", sync: true },
  });

  /* ── SiriWave ──────────────────────────────────── */
  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 700,
    style: "ios9",
    amplitude: "1.2",
    speed: "0.30",
    height: 180,
    autostart: true,
    waveColor: "#00c8ff",
  });

  /* ── Live Clock ────────────────────────────────── */
  function updateClock() {
    var now = new Date();
    var h = String(now.getHours()).padStart(2, "0");
    var m = String(now.getMinutes()).padStart(2, "0");
    var s = String(now.getSeconds()).padStart(2, "0");
    $("#status-time").text(h + ":" + m + ":" + s);
  }
  updateClock();
  setInterval(updateClock, 1000);

  /* ── Mode Manager ──────────────────────────────── */
  var MODES = {
    idle:   { icon: "◎", label: "STANDBY",   cls: "mode-idle",   statusTxt: "◎ STANDBY"   },
    listen: { icon: "●", label: "LISTENING", cls: "mode-listen", statusTxt: "● LISTENING" },
    think:  { icon: "◈", label: "THINKING",  cls: "mode-think",  statusTxt: "◈ THINKING"  },
    search: { icon: "◎", label: "SEARCHING", cls: "mode-search", statusTxt: "⊕ SEARCHING" },
    vision: { icon: "◈", label: "VISION",    cls: "mode-vision", statusTxt: "◈ VISION"    },
  };
  function setMode(mode) {
    var m = MODES[mode] || MODES.idle;
    $("body").removeClass("mode-idle mode-listen mode-think mode-search mode-vision").addClass(m.cls);
    $("#OrbStateIcon").text(m.icon);
    $("#OrbStateText").text(m.label);
    $("#status-mode").text(m.statusTxt).removeClass("mode-idle mode-listen mode-think mode-search mode-vision").addClass(m.cls);
  }
  window.setMode = setMode;
  setMode("idle");

  /* ── HUD Toast ─────────────────────────────────── */
  function showToast(msg, duration) {
    duration = duration || 2000;
    var $t = $("#HudToast");
    $t.text(msg).removeClass("hidden").addClass("toast-show");
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function () {
      $t.removeClass("toast-show");
      setTimeout(function () { $t.addClass("hidden"); }, 300);
    }, duration);
  }
  window.showToast = showToast;

  /* ── Blade panel helpers ───────────────────────── */
  function openPanel(id) {
    $("#" + id).removeAttr("hidden").addClass("panel-open");
  }
  function closePanel(id) {
    $("#" + id).removeClass("panel-open");
    setTimeout(function () { $("#" + id).attr("hidden", true); }, 400);
  }
  window.openPanel  = openPanel;
  window.closePanel = closePanel;

  // Generic close buttons (blades + drawer)
  $(document).on("click", ".blade-close-btn", function () {
    var panelId = $(this).data("panel");
    if (panelId === "ChatDrawer") {
      $("#ChatDrawer").removeClass("drawer-open");
      setTimeout(function () { $("#ChatDrawer").attr("hidden", true); }, 400);
    } else {
      closePanel(panelId);
    }
  });

  /* ── Copy buttons ──────────────────────────────── */
  $("#CopyCodeBtn").click(function () {
    navigator.clipboard.writeText($("#CodeContent").text()).then(function () {
      showToast("CODE COPIED TO CLIPBOARD");
    });
  });
  $("#CopyReportBtn").click(function () {
    navigator.clipboard.writeText($("#ReportContent").text()).then(function () {
      showToast("REPORT COPIED TO CLIPBOARD");
    });
  });

  /* ── Chat Drawer toggle ────────────────────────── */
  $("#ChatBtn").click(function () {
    if ($("#ChatDrawer").hasClass("drawer-open")) {
      $("#ChatDrawer").removeClass("drawer-open");
      setTimeout(function () { $("#ChatDrawer").attr("hidden", true); }, 400);
    } else {
      $("#ChatDrawer").removeAttr("hidden").addClass("drawer-open");
    }
  });

  /* ── Floating message ──────────────────────────── */
  var _floatTimer = null;
  function showFloatingMsg(msg) {
    clearTimeout(_floatTimer);
    $(".floating-msg").text(msg).addClass("visible");
    _floatTimer = setTimeout(function () {
      $(".floating-msg").removeClass("visible");
    }, 6000);
  }
  window.showFloatingMsg = showFloatingMsg;

  /* ── Holographic Search Nodes ──────────────────── */
  var _nodeCount = 0;
  var _nodeOffsets = [
    { top: "20%", left: "5%"  },
    { top: "45%", left: "3%"  },
    { top: "20%", right: "5%" },
    { top: "55%", right: "4%" },
    { top: "70%", left: "8%"  },
  ];

  function createSearchNode(title, content, url) {
    var idx  = _nodeCount % _nodeOffsets.length;
    var pos  = _nodeOffsets[idx];
    var id   = "snode-" + (++_nodeCount);

    var posStyle = "";
    for (var k in pos) posStyle += k + ":" + pos[k] + ";";

    var urlHtml = url ? '<div class="search-node-url">' + url + '</div>' : '';

    var $node = $('<div class="search-node" id="' + id + '" style="' + posStyle + '">' +
      '<div class="search-node-header">' +
        '<span class="search-node-title">' + (title || "SEARCH RESULT") + '</span>' +
        '<button class="search-node-close" data-nodeid="' + id + '">✕</button>' +
      '</div>' +
      '<div class="search-node-body">' + (content || "") + '</div>' +
      urlHtml +
    '</div>');

    $("#SearchNodesContainer").append($node);

    // Make draggable
    makeDraggable($node[0]);

    return id;
  }
  window.createSearchNode = createSearchNode;

  function dismissSearchNode(id) {
    var $n = $("#" + id);
    $n.addClass("dissolving");
    setTimeout(function () { $n.remove(); }, 380);
  }

  $(document).on("click", ".search-node-close", function () {
    var id = $(this).data("nodeid");
    dismissSearchNode(id);
  });

  // Drag logic for search nodes
  function makeDraggable(el) {
    var startX, startY, startLeft, startTop;
    $(el).find(".search-node-header").on("mousedown", function (e) {
      e.preventDefault();
      startX = e.clientX; startY = e.clientY;
      var rect = el.getBoundingClientRect();
      startLeft = rect.left; startTop = rect.top;
      // Switch to absolute pixel positioning
      $(el).css({ left: startLeft + "px", top: startTop + "px", right: "auto", bottom: "auto" });

      $(document).on("mousemove.drag", function (e2) {
        var dx = e2.clientX - startX;
        var dy = e2.clientY - startY;
        $(el).css({ left: (startLeft + dx) + "px", top: (startTop + dy) + "px" });
      });
      $(document).on("mouseup.drag", function () {
        $(document).off("mousemove.drag mouseup.drag");
      });
    });
  }

  /* ── Mic Button ────────────────────────────────── */
  $("#MicBtn").click(function () {
    setMode("listen");
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").removeAttr("hidden");
    eel.takeAllCommands()();
  });

  /* ── Keyboard shortcut ⌘J ──────────────────────── */
  document.addEventListener("keyup", function (e) {
    if (e.key === "j" && e.metaKey) {
      setMode("listen");
      eel.play_assistant_sound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").removeAttr("hidden");
      eel.takeAllCommands()();
    }
  }, false);

  /* ── Show/Hide send vs mic ─────────────────────── */
  function ShowHideButton(message) {
    if (message.length === 0) {
      $("#MicBtn").removeAttr("hidden");
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").removeAttr("hidden");
    }
  }

  /* ── Play assistant with text ──────────────────── */
  function PlayAssistant(message) {
    if (message.trim() !== "") {
      setMode("think");
      $("#Oval").attr("hidden", true);
      $("#SiriWave").removeAttr("hidden");
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#MicBtn").removeAttr("hidden");
      $("#SendBtn").attr("hidden", true);
    }
  }

  $("#chatbox").keyup(function () { ShowHideButton($(this).val()); });
  $("#SendBtn").click(function () { PlayAssistant($("#chatbox").val()); });
  $("#chatbox").keypress(function (e) { if (e.which === 13) PlayAssistant($(this).val()); });
  $("#TextInput").click(function () { $("#chatbox").focus(); });

});