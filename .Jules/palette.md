# Palette's Journal

This journal documents critical UX and accessibility learnings discovered while working on this application.

## 2026-07-22 - Inputs Require Explicit and Accessible Labeling
**Learning:** Simply placing placeholders in text input fields is highly inaccessible for screen reader users and leads to a cognitive disconnect once the user begins typing, as the visual description disappears. Explicitly linking label tags with form inputs via corresponding `for` and `id` attributes ensures assistive technologies can correctly announce input purpose and context.
**Action:** Always wrap form text fields with descriptive `<label>` elements. Use a visually consistent style (e.g., small, bold headers above the inputs) rather than relying solely on placeholder text.

## 2026-07-22 - Prevent Duplicate Async Form Submissions and Provide Active Feedback
**Learning:** Users often double-click or repeatedly tap submit buttons when there is no immediate visual or interactive block on the button. Disabling the button immediately upon trigger and updating its text content provides a clear, tactile state change, eliminating duplicate API payloads and enhancing the sense of system responsiveness.
**Action:** Implement immediate disabled-state class changes and loading messages inside button handlers for all asynchronous backend operations.
