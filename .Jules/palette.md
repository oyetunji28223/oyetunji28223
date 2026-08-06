# Palette's Journal - Critical UX/Accessibility Learnings

## 2025-02-18 - [Preventing API Spam with Async Button States]
**Learning:** In highly asynchronous simulations where UI updates rely on backend network roundtrips, failing to manage button states creates visual confusion and makes the app vulnerable to duplicate request submissions (spamming clicks). Disabling the trigger button and updating its text to reflect loading states provides clear visual cue and keeps the backend inputs idempotent and resilient.
**Action:** Always wrap async handlers with disabled button transitions and temporary visual status labels to protect the API and maintain focus.

## 2026-08-04 - [Dashboard Auto-Refresh and Background Polling Control]
**Learning:** Real-time dashboards monitoring active background simulators must offer clear user control over updates. Coupling a manual trigger with an easily toggled auto-refresh checkbox allows users to comfortably observe rapid state updates without manual fatigue, while also preventing unnecessary network polling when disabled.
**Action:** Provide explicit auto-refresh checkboxes for real-time status modules, and ensure background intervals are safely disposed of on page unload.

## 2026-08-05 - [Interactive List Item Quick Actions]
**Learning:** In dashboards listing key record identifiers (like long cryptographic wallet addresses), manual copy-pasting or re-typing to filter associated detail cards introduces high friction and human error. Providing a context-specific quick action like a '📋 Use Wallet' button inside list items that copies the ID to the clipboard, updates independent search inputs, and auto-triggers lookup operations instantly bridges dashboard modules for an integrated, satisfying user flow.
**Action:** Always provide simple quick action buttons next to read-only record lists to automatically transfer context and accelerate operational tasks.
