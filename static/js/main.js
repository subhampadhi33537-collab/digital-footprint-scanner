/**
 * ======================================================
 * main.js
 * ------------------------------------------------------
 * Monolithic JS for Digital Footprint Scanner
 *
 * Responsibilities:
 *  - Validator utilities (merged)
 *  - Index page scan form handling (/scan)
 *  - Dashboard rendering & refresh (sessionStorage, /dashboard-data, /data/result.json)
 *  - AI chatbot modal and communication (/ai-assistant)
 *  - Loaders, error handling, normalization, escaping
 *
 * Usage:
 *  - Drop this file at /static/js/main.js
 *  - Include <script src="/static/js/main.js"></script> in your HTML
 *
 * Notes:
 *  - This file intentionally checks for presence of elements in DOM and only runs
 *    page-specific code when necessary — safe to include on all pages.
 *  - It tries to be resilient against inconsistent backend shapes.
 * ======================================================
 */

(function () {
  "use strict";

  /* ======================================================
     VALIDATOR (Merged from utils/validator.js)
     Exposed as window.Validator
  ====================================================== */

  function _isEmpty(value) {
    return (
      value === null ||
      value === undefined ||
      typeof value !== "string" ||
      value.trim().length === 0
    );
  }

  function _normalize(value) {
    if (typeof value !== "string") return "";
    return value.trim();
  }

  function _sanitizeInput(value) {
    if (typeof value !== "string") return "";
    // Basic XSS-safe removal of dangerous characters for this app
    return value
      .replace(/</g, "")
      .replace(/>/g, "")
      .replace(/"/g, "")
      .replace(/'/g, "")
      .replace(/`/g, "")
      .replace(/\//g, "")
      .trim();
  }

  function _isValidEmail(email) {
    if (_isEmpty(email)) return false;
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  function _isGmailAddress(email) {
    if (!_isValidEmail(email)) return false;
    return email.toLowerCase().endsWith("@gmail.com");
  }

  function _isValidUsername(username) {
    if (_isEmpty(username)) return false;
    // 3-30 chars, letters numbers . _ -
    const usernameRegex = /^[a-zA-Z0-9._-]{3,30}$/;
    return usernameRegex.test(username);
  }

  function _validateScanInput(rawInput) {
    const cleanInput = _sanitizeInput(rawInput);
    if (_isEmpty(cleanInput)) {
      return { valid: false, error: "Input cannot be empty" };
    }
    // Email case
    if (cleanInput.includes("@")) {
      if (!_isGmailAddress(cleanInput)) {
        return { valid: false, error: "Only valid Gmail IDs are allowed" };
      }
      return { valid: true, type: "email", value: cleanInput };
    }
    // Username case
    if (!_isValidUsername(cleanInput)) {
      return {
        valid: false,
        error: "Invalid username. Use 3–30 characters (letters, numbers, . _ -)",
      };
    }
    return { valid: true, type: "username", value: cleanInput };
  }

  function _validateChatMessage(message) {
    const clean = _sanitizeInput(message);
    if (_isEmpty(clean)) return { valid: false, error: "Message cannot be empty" };
    if (clean.length < 2) return { valid: false, error: "Message is too short" };
    if (clean.length > 500) return { valid: false, error: "Message too long (max 500 characters)" };
    return { valid: true, value: clean };
  }

  function _isValidApiResponse(data) {
    return data !== null && typeof data === "object" && !Array.isArray(data);
  }

  function _validateScanResult(data) {
    if (!_isValidApiResponse(data)) return false;
    return ("platforms" in data) && ("risk_level" in data) && ("exposures" in data);
  }

  function _showInputError(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.classList.remove("hidden");
  }

  function _hideInputError(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = "";
    el.classList.add("hidden");
  }

  // Export validator to window so page code can use it
  window.Validator = {
    isEmpty: _isEmpty,
    normalize: _normalize,
    sanitizeInput: _sanitizeInput,
    isValidEmail: _isValidEmail,
    isGmailAddress: _isGmailAddress,
    isValidUsername: _isValidUsername,
    validateScanInput: _validateScanInput,
    validateChatMessage: _validateChatMessage,
    isValidApiResponse: _isValidApiResponse,
    validateScanResult: _validateScanResult,
    showInputError: _showInputError,
    hideInputError: _hideInputError,
  };

  /* ======================================================
     UTILS
  ====================================================== */

  function _id(...candidates) {
    for (let i = 0; i < candidates.length; i++) {
      if (!candidates[i]) continue;
      const el = document.getElementById(candidates[i]);
      if (el) return el;
    }
    return null;
  }

  function _safeJSONParse(s) {
    try {
      return JSON.parse(s);
    } catch {
      return null;
    }
  }

  function _escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function _createEl(tag, options = {}) {
    const el = document.createElement(tag);
    if (options.className) el.className = options.className;
    if (options.text) el.textContent = options.text;
    if (options.html) el.innerHTML = options.html;
    if (options.attrs) {
      Object.keys(options.attrs).forEach((k) => el.setAttribute(k, options.attrs[k]));
    }
    return el;
  }

  function _normalizeScanResponse(raw) {
    if (!raw) return null;
    // If server returns { scan_results: {...}, risk_results: {...} }
    if (raw.scan_results && typeof raw.scan_results === "object") {
      return raw.scan_results;
    }
    // If server returns { platforms: ..., risk_level: ... } directly
    if (_validateScanResult(raw)) return raw;
    // Some servers may return nested shapes
    if (raw.platforms || raw.exposures || raw.risk_level || raw.correlations) {
      return raw;
    }
    // If object has scan_results nested deeper
    for (const k in raw) {
      if (raw[k] && typeof raw[k] === "object" && _validateScanResult(raw[k])) {
        return raw[k];
      }
    }
    return null;
  }

  // small delay helper
  function _sleep(ms) {
    return new Promise((res) => setTimeout(res, ms));
  }

  /* ======================================================
     DOMContentLoaded main initialization
  ====================================================== */

  document.addEventListener("DOMContentLoaded", () => {
    // Run initialization after DOM ready
    initApp();
  });

  /* ======================================================
     Main - initApp
  ====================================================== */

  async function initApp() {
    // Initialize modules conditionally
    initScanModule();
    initDashboardModule();
    initChatbotModule();
    initGlobalHelpers();
  }

  /* ======================================================
     SCAN MODULE (index.html)
     - Handles form submission, validation, scanning
  ====================================================== */

  function initScanModule() {
    const scanForm = _id("scanForm", "scan-form");
    const scanInput = _id("user_input", "scan-input");
    const inputErrorId = "input-error";
    const inputErrorEl = _id(inputErrorId);

    if (!scanForm || !scanInput) {
      // Not on index page
      return;
    }

    // Ensure submit button exists
    const submitBtn = scanForm.querySelector('button[type="submit"]') || scanForm.querySelector("button");

    // Attach submit handler
    scanForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      _hideInputError(inputErrorId);

      const userValue = scanInput.value || "";
      const validation = window.Validator.validateScanInput(userValue);
      if (!validation.valid) {
        window.Validator.showInputError(inputErrorId, validation.error);
        return;
      }

      scanInput.setAttribute("disabled", "disabled");
      if (submitBtn) submitBtn.setAttribute("disabled", "disabled");

      let loader = _id("scan-inline-loader");
      if (!loader) {
        loader = _createEl("div", { className: "mt-4 text-indigo-600", text: "Scanning... Please wait ⏳" });
        loader.id = "scan-inline-loader";
        scanForm.appendChild(loader);
      }
      loader.style.display = "block";

      try {
        const res = await fetch("/scan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_input: validation.value }),
          credentials: "same-origin",
        });

        const json = await res.json().catch(() => null);

        if (!res.ok || !json) {
          window.Validator.showInputError(inputErrorId, "Scan failed or invalid response.");
          return;
        }

        // ⚡ Store in sessionStorage BEFORE navigating
        const normalized = _normalizeScanResponse(json) || json;
        sessionStorage.setItem("scanResult", JSON.stringify(normalized));

        // Navigate AFTER storing
        // Navigate AFTER storing
        window.location.href = "/dashboard"; // Use Flask route
        // Use the same path as your static file
      } catch (err) {
        window.Validator.showInputError(inputErrorId, "Network error. Try again.");
      } finally {
        scanInput.removeAttribute("disabled");
        if (submitBtn) submitBtn.removeAttribute("disabled");
        if (loader) loader.style.display = "none";
      }
    });


    // Enter key support
    scanInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        scanForm.requestSubmit();
      }
    });

    // Hide errors while typing
    scanInput.addEventListener("input", () => {
      _hideInputError(inputErrorId);
    });
  }
  /* ======================================================
     DASHBOARD MODULE (dashboard.html)
     - Robust loading from sessionStorage, backend, or static JSON
     - Renders platforms, exposures, risk, correlations
  ====================================================== */
  function initDashboardModule() {
    const platformsContainer = _id("platforms-container");
    const exposurePersonal = _id("personal-exposure");
    const exposureContact = _id("contact-exposure");
    const exposureOnline = _id("online-exposure");
    const riskLevelEl = _id("risk-level");
    const correlationList = _id("correlation-list");
    const dashboardError = _id("dashboard-error");
    const refreshBtn = _id("refreshDashboard");

    if (!platformsContainer && !exposurePersonal && !riskLevelEl) return; // Not a dashboard page

    let scanData = null;

    // Helper: show error
    function showDashboardError(msg) {
      if (dashboardError) {
        dashboardError.textContent = msg;
        dashboardError.classList.remove("hidden");
      } else {
        console.warn("Dashboard error:", msg);
      }
    }

    // 1️⃣ Load from sessionStorage
    try {
      const raw = sessionStorage.getItem("scanResult");
      if (raw) scanData = _safeJSONParse(raw);
    } catch { scanData = null; }

    // 2️⃣ Fetch backend session
    async function fetchDashboardFromServer() {
      try {
        const res = await fetch("/dashboard-data", { cache: "no-store", credentials: "same-origin" });
        if (!res.ok) return null;
        const json = await res.json().catch(() => null);
        if (!json) return null;
        return json;
      } catch {
        return null;
      }
    }

    // 3️⃣ Fetch static JSON
    async function fetchStaticResult() {
      try {
        const res = await fetch("/static/data/results.json", { cache: "no-store" });
        if (!res.ok) return null;
        const json = await res.json().catch(() => null);
        return json || null;
      } catch {
        return null;
      }
    }

    // Normalize and store
    function normalizeAndStore(raw) {
      if (!raw) return null;
      const normalized = _normalizeScanResponse(raw) || raw;
      try {
        sessionStorage.setItem("scanResult", JSON.stringify(normalized));
      } catch { }
      return normalized;
    }

    // Load dashboard
    async function loadDashboard() {
      if (!scanData) {
        scanData = normalizeAndStore(await fetchDashboardFromServer());
      }
      if (!scanData) {
        scanData = normalizeAndStore(await fetchStaticResult());
      }
      if (!scanData) {
        showDashboardError("No scan data found. Please run a scan.");
        return;
      }
      renderAll(scanData);
    }

    // Render everything
    function renderAll(data) {
      renderPlatforms(data.platforms || []);
      renderExposures(data.exposures || {});
      renderRisk(data.risk_level || "UNKNOWN");
      renderCorrelations(data.correlations || []);
    }

    function renderPlatforms(platforms) {
      if (!platformsContainer) return;
      platformsContainer.innerHTML = "";
      if (!platforms.length) {
        platformsContainer.appendChild(_createEl("div", { html: "<em>No platforms detected</em>" }));
        return;
      }
      platforms.forEach(p => {
        const name = p.name || p.platform || "Unknown";
        const found = !!p.found;
        const card = _createEl("div", { className: "bg-white p-4 rounded-xl shadow hover:shadow-xl transition mb-3" });
        card.innerHTML = `
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <h4 class="font-semibold text-indigo-600">${_escapeHtml(name)}</h4>
            ${p.summary ? `<p class="text-sm text-gray-600">${_escapeHtml(p.summary)}</p>` : ""}
            ${p.details ? `<p class="text-xs text-gray-500 mt-2">${_escapeHtml(p.details)}</p>` : ""}
          </div>
          <div class="flex-shrink-0">
            <span class="px-3 py-1 text-sm rounded-full ${found ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'}">
              ${found ? 'Found' : 'Not Found'}
            </span>
          </div>
        </div>
      `;
        platformsContainer.appendChild(card);
      });
    }

    function renderExposures(exposures) {
      if (exposurePersonal) exposurePersonal.innerHTML = "";
      if (exposureContact) exposureContact.innerHTML = "";
      if (exposureOnline) exposureOnline.innerHTML = "";
      (exposures.personal || []).forEach(i => { if (exposurePersonal) exposurePersonal.innerHTML += `<li>${_escapeHtml(i)}</li>`; });
      (exposures.contact || []).forEach(i => { if (exposureContact) exposureContact.innerHTML += `<li>${_escapeHtml(i)}</li>`; });
      (exposures.online || []).forEach(i => { if (exposureOnline) exposureOnline.innerHTML += `<li>${_escapeHtml(i)}</li>`; });
    }

    function renderRisk(level) {
      if (!riskLevelEl) return;
      const text = String(level).toUpperCase();
      let cls = "inline-block px-4 py-2 rounded-full text-white text-sm ";
      cls += text === "LOW" ? "bg-green-600" : text === "MEDIUM" ? "bg-yellow-500" : text === "HIGH" ? "bg-red-600" : "bg-gray-600";
      riskLevelEl.className = cls;
      riskLevelEl.textContent = text;
    }

    function renderCorrelations(list) {
      if (!correlationList) return;
      correlationList.innerHTML = "";
      if (!list.length) {
        correlationList.innerHTML = "<li>No correlations detected</li>";
        return;
      }
      list.forEach(c => {
        const li = document.createElement("li");
        li.textContent = typeof c === "string" ? c : JSON.stringify(c);
        correlationList.appendChild(li);
      });
    }

    // Refresh button
    if (refreshBtn) {
      refreshBtn.addEventListener("click", async () => {
        const newData = normalizeAndStore(await fetchDashboardFromServer() || await fetchStaticResult());
        if (newData) renderAll(newData);
        else showDashboardError("Failed to refresh dashboard.");
      });
    }

    // Initial load
    loadDashboard();
  }

/* ======================================================
   CHATBOT MODULE
   - modal open/close
   - handles sending messages to /ai-assistant
   - styled chat bubbles with emojis 😎You / 🤖AI
====================================================== */

function initChatbotModule() {
    const chatbotBtn = _id("chatbotBtn");
    const chatbotModal = _id("chatbotModal");
    const closeModal = _id("closeModal");
    const chatBox = _id("chatBox");
    const userMessage = _id("userMessage");
    const sendMessageBtn = _id("sendMessage");
    const chatError = _id("chat-error");

    if (!chatbotBtn || !chatbotModal || !closeModal || !chatBox || !userMessage || !sendMessageBtn) {
        // Not on a page with chatbot
        return;
    }

    // =======================
    // Modal Open/Close
    // =======================
    function openModal() {
        chatbotModal.classList.remove("hidden");
        chatbotModal.classList.add("flex");
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function closeModalFn() {
        chatbotModal.classList.add("hidden");
        chatbotModal.classList.remove("flex");
    }

    chatbotBtn.addEventListener("click", openModal);
    closeModal.addEventListener("click", closeModalFn);
    chatbotModal.addEventListener("click", (e) => {
        if (e.target === chatbotModal) closeModalFn();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeModalFn();
    });

    // =======================
    // Append Chat Message
    // =======================
    function appendMessage(sender, text) {
        const wrapper = _createEl("div", { className: "mb-2 flex" });

        let label = "";
        let bubbleClasses = "text-sm whitespace-pre-wrap p-2 rounded-lg max-w-[70%]";

        if (sender === "You") {
            label = "😎 You";
            wrapper.classList.add("justify-end");
            bubbleClasses += " bg-indigo-600 text-white";
        } else {
            label = "🤖 AI";
            wrapper.classList.add("justify-start");
            bubbleClasses += " bg-gray-200 text-gray-900";
        }

        const who = _createEl("div", { className: "font-semibold text-sm mb-1", text: label });
        const content = _createEl("div", { className: bubbleClasses, text: text });

        // User on right, AI on left
        wrapper.appendChild(content);
        wrapper.appendChild(who);
        chatBox.appendChild(wrapper);

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // =======================
    // Error Handling
    // =======================
    function showChatError(msg) {
        if (!chatError) {
            console.warn("Chat error:", msg);
            return;
        }
        chatError.textContent = msg;
        chatError.classList.remove("hidden");
    }

    function hideChatError() {
        if (!chatError) return;
        chatError.textContent = "";
        chatError.classList.add("hidden");
    }

    // =======================
    // Send Message
    // =======================
    async function sendChatMessage() {
        hideChatError();
        const raw = userMessage.value || "";
        const validation = window.Validator.validateChatMessage(raw);
        if (!validation.valid) {
            showChatError(validation.error);
            return;
        }
        const msg = validation.value;

        // Append user message
        appendMessage("You", msg);
        userMessage.value = "";

        // Loader bubble
        const loader = _createEl("div", {
            className: "mb-2 flex justify-start",
        });
        const loaderBubble = _createEl("div", {
            className: "bg-gray-300 text-gray-700 text-sm p-2 rounded-lg animate-pulse",
            text: "🤖 AI is typing..."
        });
        loader.appendChild(loaderBubble);
        chatBox.appendChild(loader);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const res = await fetch("/ai-assistant", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg }),
                credentials: "same-origin",
            });

            const json = await res.json().catch(() => null);
            loader.remove();

            if (!res.ok) {
                const errMsg = (json && (json.error || json.message)) || `AI error (${res.status})`;
                showChatError(errMsg);
                return;
            }

            const reply = (json && json.reply) || "No response from AI";
            appendMessage("AI", reply);

        } catch (err) {
            loaderBubble.textContent = "AI service unavailable. Try again later.";
            console.error("ai-assistant error:", err);
        }
    }

    sendMessageBtn.addEventListener("click", sendChatMessage);
    userMessage.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
}

  /* ======================================================
     GLOBAL HELPERS / OPTIONAL FEATURES
  ====================================================== */

  function initGlobalHelpers() {
    // If developer wants auto-refresh of dashboard every X seconds, toggle here
    const enableAutoRefresh = false; // set true to enable
    const autoRefreshIntervalMs = 3 * 60 * 1000; // 3 minutes

    if (enableAutoRefresh) {
      setInterval(async () => {
        const refreshBtn = _id("refreshDashboard");
        if (refreshBtn) refreshBtn.click();
      }, autoRefreshIntervalMs);
    }

    // Console summary for debugging
    console.info("main.js loaded: Validator available as window.Validator. Modules initialized if relevant DOM nodes exist.");
  }

  // Expose a debugging function optionally
  window.__dfs_debug = {
    clearSessionScanResult: function () {
      try {
        sessionStorage.removeItem("scanResult");
        console.info("sessionStorage.scanResult cleared");
      } catch (e) {
        console.warn("Unable to clear sessionStorage.scanResult", e);
      }
    },
    dumpSessionScanResult: function () {
      try {
        const raw = sessionStorage.getItem("scanResult");
        console.log("scanResult:", raw ? JSON.parse(raw) : null);
      } catch (e) {
        console.warn("dump error", e);
      }
    },
  };

  /* ======================================================
     END OF FILE
  ====================================================== */
})();
