# Palette's Journal

## 2025-07-27 - Semantic Forms and Screen Reader Feedback for Async Crypto Simulation
**Learning:** Simulation dashboards that rely on click-only div inputs prevent natural keyboard form submission (pressing "Enter"). Lacking assistive technologies (aria-live) makes it impossible for screen reader users to know when state changes (like "Registering...") occur on async operations.
**Action:** Always wrap input-button groups in semantic `<form>` tags, bind to the `submit` event instead of `click`, and apply `aria-live="polite"` to status regions.
