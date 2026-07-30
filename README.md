# Phantom AI God Mode — Billion Dollar Engine

## Overview

- **Autonomous backend** designed to simulate targeting $1B/week profit per wallet lineage by scaling trading/farming and wallet cloning infinitely after wallet collection.
- All actions (collection, trading, compounding, scaling, profit sending) are fully automatic within the simulation.
- Each registered wallet initiates its own independent cycle of profit generation and scaling.

## How To Run

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` includes `fastapi`, `uvicorn`, `pydantic`. For testing, it also includes `pytest` and `httpx`.)

2.  **Configure (Optional):**
    - The weekly profit target per wallet can be set using the environment variable `BILLION_TARGET_AMOUNT`. It defaults to `1000000000` ($1 Billion).
      ```bash
      export BILLION_TARGET_AMOUNT="500000000" # Example: Set target to $500 Million
      ```

3.  **Run the Application:**
    ```bash
    uvicorn backend.billion_engine:app --reload --host 0.0.0.0 --port 8000
    ```
    (Added host and port for clarity, common for local dev)

## API Usage

-   **Register a wallet:**
    Starts the autonomous profit generation and scaling cycle for the given wallet.
    ```bash
    curl -X POST http://localhost:8000/collect_wallet -H 'Content-Type: application/json' -d '{"wallet":"YourPhantomWalletHere"}'
    ```

-   **Get profit events for a wallet:**
    Retrieves a list of simulated profit events for a specific wallet.
    ```bash
    curl http://localhost:8000/profit_events?wallet=YourPhantomWalletHere
    ```

-   **Check system status:**
    Shows all registered wallets, their current individual scaling factors, and all profit events.
    ```bash
    curl http://localhost:8000/status
    ```
    *(Note: The `scaling_factor` is now per-wallet, visible in `wallet_scaling_factors` within the response).*

-   **Adjust scaling factor for a wallet (New):**
    Manually sets the scaling factor for a specific, already registered wallet. The factor must be a positive number.
    ```bash
    curl -X POST http://localhost:8000/adjust_scaling_factor -H 'Content-Type: application/json' -d '{"wallet":"YourPhantomWalletHere", "new_factor": 1.5}'
    ```

## How It Works

-   Every new wallet registered via `/collect_wallet` triggers an independent, infinite, auto-scaling, compounding AI farming/trading simulation loop (`billion_cycle`). Each new wallet is **randomly assigned** one of several predefined (simulated) trading strategies (e.g., LOW_RISK, MEDIUM_RISK, HIGH_RISK).
-   The profit generation within the `billion_cycle` is directly influenced by the wallet's assigned strategy, which defines parameters like base profit amounts and potential profit ranges.
-   **Dynamic Strategy Adaptation:** If a wallet's simulation with its current strategy fails to make significant progress over several cycles (and isn't already close to its weekly target), it will automatically attempt to switch to a different, randomly chosen strategy to improve its chances. The scaling factor is maintained during such a switch. This allows the simulation to be more adaptive.
-   Each loop aims to hit the `BILLION_TARGET_AMOUNT` weekly.
-   If the target is not met (and strategy adaptation hasn't occurred or is also not helping sufficiently), the wallet's `scaling_factor` (simulating increased volume/risk) is doubled, and it may clone itself. The clone **inherits the parent's current strategy** and the new, higher scaling factor, then starts its own independent `billion_cycle`.
-   Once a wallet's cycle hits the weekly target, its `scaling_factor` and weekly total reset for the next simulated week.
-   All profits are simulated as USDC sent to wallets (logged by the application).
-   The system uses in-memory storage, so all data is reset if the application restarts.

## Basic HTML Frontend (New)

A simple HTML frontend is available in the `frontend/` directory to interact with the API.

### How To Use the Frontend:

1.  **Start the Backend Server:** Ensure the Python FastAPI backend is running (see "How To Run" section above). It typically runs on `http://localhost:8000`.
2.  **Open `index.html`:**
    *   Navigate to the `frontend/` directory in your file explorer.
    *   Open the `index.html` file directly in your web browser (e.g., by double-clicking it, or using "File > Open" in your browser).
3.  **Interact:**
    *   The page will provide fields and buttons to:
        *   Register new wallets.
        *   View the overall system status.
        *   Fetch and display profit events for specific wallets.

**Note:** This frontend is a basic example for demonstration and interaction. It makes direct API calls to the backend. Ensure your browser allows requests to `http://localhost:8000` from a `file:///` URL if you open it directly, or consider serving the `frontend` directory via a simple local HTTP server for more robust behavior (though direct file opening should work for this simple case if the backend is on localhost).

---
