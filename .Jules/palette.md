# Palette's Journal - Critical UX/Accessibility Learnings

## 2025-02-18 - [Preventing API Spam with Async Button States]
**Learning:** In highly asynchronous simulations where UI updates rely on backend network roundtrips, failing to manage button states creates visual confusion and makes the app vulnerable to duplicate request submissions (spamming clicks). Disabling the trigger button and updating its text to reflect loading states provides clear visual cue and keeps the backend inputs idempotent and resilient.
**Action:** Always wrap async handlers with disabled button transitions and temporary visual status labels to protect the API and maintain focus.

## 2025-02-18 - [Eliminating XSS Risks via Safe DOM APIs]
**Learning:** Constructing HTML dynamically using string interpolation with user-supplied values (such as wallet addresses or simulated transaction IDs) and inserting it using `innerHTML` introduces serious Cross-Site Scripting (XSS) vulnerabilities. Utilizing safe DOM APIs like `document.createElement` and `textContent` guarantees that values are safely treated as plain text by the browser, rendering them securely and correctly.
**Action:** Always prefer safe DOM construction methods over `innerHTML` string interpolation when handling any dynamic or potentially user-supplied payload.
