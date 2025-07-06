# Agent Guidelines for "Phantom AI Billion Dollar Engine"

This document provides guidelines for AI agents (like Jules) working on this project.

## 1. Project Overview

*   **Nature:** This project, "Phantom AI Billion Dollar Engine," is a **simulation** of an autonomous backend for cryptocurrency trading, farming, and wallet scaling. It is not intended for use with real funds or on mainnets.
*   **Core Logic:** The main application is `backend/billion_engine.py`, a FastAPI server that simulates wallet operations.
*   **Primary Goal:** To model and simulate complex, automated financial strategies. Focus on the logic, scalability of the simulation, and clarity of the simulation's operations.

## 2. Development Practices

### 2.1. Coding Style
*   **Python:** Adhere to [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).
    *   Use a linter/formatter like Black or Ruff if possible to maintain consistency.
    *   Prioritize readability and clarity in code.
*   **Comments & Docstrings:**
    *   Write clear docstrings for all public modules, classes, functions, and methods.
    *   Use inline comments to explain complex logic or non-obvious decisions.

### 2.2. Testing
*   **Requirement:** All new features or significant modifications to existing logic **must** be accompanied by unit tests.
*   **Framework:** Use `pytest` for testing. Tests are located in the `/tests` directory.
*   **Coverage:** Aim for good test coverage, especially for critical logic within `billion_cycle` and API endpoints.
*   **Running Tests:** Refer to `README.md` for instructions on installing test dependencies. Run tests using `pytest` from the project root.

### 2.3. Commit Messages
*   Follow conventional commit message formats (e.g., a short subject line, blank line, then detailed body if needed).
*   Example: `feat: Add endpoint for manual scaling factor adjustment`

### 2.4. Dependencies
*   All Python dependencies should be listed in `requirements.txt`.
*   Keep dependencies updated where feasible, but ensure compatibility.

## 3. Running the Application
*   Refer to the `README.md` file for detailed instructions on setting up the environment and running the application.

## 4. Code Structure
*   **Backend Application:** `backend/billion_engine.py`
*   **Tests:** `/tests`
*   **Configuration:** Primarily through environment variables (e.g., `BILLION_TARGET_AMOUNT`). Avoid hardcoding configurable values.
*   **Logging:** Use the standard `logging` module for application logs. Avoid `print()` statements for operational logging.

## 5. Specific Considerations
*   **`billion_cycle`:** This is the core simulation loop. Changes here should be made carefully and tested thoroughly, especially regarding its asynchronous nature, state management, and scaling/cloning logic.
*   **State Management:** The application currently uses in-memory data structures for state (`wallets`, `profit_events`, `wallet_scaling_factors`). Be mindful of this if proposing features that require persistence.

## 6. Interaction
*   If instructions are unclear or a task significantly deviates from the current plan or project scope, please ask for clarification using `request_user_input`.
*   Always update the plan using `set_plan` if changes are needed.
*   Provide clear `plan_step_complete` messages.

By following these guidelines, we can ensure the project remains maintainable, understandable, and robust (within its simulation context).
