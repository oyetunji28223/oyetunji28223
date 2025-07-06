import asyncio
import random
import logging # Added
import os # Added
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

import fastapi # Added for HTTPException
# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="Phantom AI Billion Dollar Engine", version="1.0.0")

# In-memory storage for simplicity. In a real application, use a database.
wallets: List[str] = [] # Stores registered wallet addresses
profit_events: Dict[str, List[Dict]] = {} # Stores simulated profit events per wallet
wallet_scaling_factors: Dict[str, float] = {} # Stores current scaling factor per wallet

class WalletRequest(BaseModel):
    """Request model for collecting a new wallet."""
    wallet: str

class AdjustScalingFactorRequest(BaseModel):
    """Request model for adjusting a wallet's scaling factor."""
    wallet: str
    new_factor: float

@app.post("/collect_wallet", summary="Register a new wallet and start its billion cycle simulation.")
async def collect_wallet(req: WalletRequest):
    """
    Registers a new wallet if not already present and initiates its autonomous profit generation cycle.
    Each wallet operates independently.
    """
    if req.wallet not in wallets:
        wallets.append(req.wallet)
        wallet_scaling_factors[req.wallet] = 1.0 # Initialize scaling factor for the new wallet
        logging.info(f"Wallet {req.wallet} registered. Starting billion cycle.")
        asyncio.create_task(billion_cycle(req.wallet, initial_scaling_factor=1.0))
    else:
        logging.info(f"Wallet {req.wallet} already registered.")
    return {"status": "registered", "wallet": req.wallet}

async def billion_cycle(wallet: str, initial_scaling_factor: float):
    """
    Main asynchronous loop for a single wallet simulating profit generation,
    sending profits, and scaling operations.
    """
    # global scaling_factor # Removed
    current_scaling_factor = initial_scaling_factor
    clone_count = 0
    try:
        billion_target_str = os.environ.get("BILLION_TARGET_AMOUNT", "1000000000")
        billion_target = int(billion_target_str)
    except ValueError:
        logging.error(f"Invalid BILLION_TARGET_AMOUNT: {os.environ.get('BILLION_TARGET_AMOUNT')}. Using default 1,000,000,000.")
        billion_target = 1_000_000_000
    weekly_total = 0
    logging.info(f"Starting billion_cycle for wallet: {wallet} with initial_scaling_factor: {initial_scaling_factor}, Target: {billion_target}")
    while True:
        try:
            # 1. Simulate compounding trading/farming (risk and volume increase over time)
            await asyncio.sleep(random.randint(2, 5)) # Simulate time for trading/farming
            profit_amount = round(random.uniform(100_000, 300_000) * current_scaling_factor, 2)
            profit = {
                "id": f"{wallet}_evt_{random.randint(10000,99999)}",
                "amount": profit_amount,
                "sent": False
            }
            profit_events.setdefault(wallet, []).append(profit)
            wallet_scaling_factors[wallet] = current_scaling_factor # Update status dict
            weekly_total += profit["amount"]
            logging.info(f"Wallet {wallet}: Generated profit {profit_amount}, Weekly total: {weekly_total}, Scaling: {current_scaling_factor}")

            # 2. Auto-send (simulate)
            await asyncio.sleep(2) # Simulate time for sending profit
            profit["sent"] = True
            logging.info(f"Wallet {wallet}: Profit {profit_amount} USDC sent.")

            # 3. Aggressive scaling: clone, double, and recurse
            if weekly_total < billion_target:
                current_scaling_factor *= 2
                wallet_scaling_factors[wallet] = current_scaling_factor # Update status dict
                logging.info(f"Wallet {wallet}: Scaling factor doubled to {current_scaling_factor}")

                clone_wallet = f"{wallet}_clone_{clone_count+1}"
                if clone_wallet not in wallets:
                    logging.info(f"Wallet {wallet}: Cloning to {clone_wallet} with scaling factor {current_scaling_factor}")
                    wallets.append(clone_wallet)
                    wallet_scaling_factors[clone_wallet] = current_scaling_factor # Initialize for new clone
                    asyncio.create_task(billion_cycle(clone_wallet, initial_scaling_factor=current_scaling_factor))
                    clone_count += 1
            else:
                logging.info(f"Wallet {wallet}: 🎉 Reached $1B target this week! Resetting weekly total and scaling factor.")
                weekly_total = 0
                current_scaling_factor = 1.0 # Reset for this wallet's next week
                wallet_scaling_factors[wallet] = current_scaling_factor # Update status dict

            await asyncio.sleep(random.randint(3, 7)) # Simulate time until next cycle iteration
        except asyncio.CancelledError:
            logging.info(f"Billion_cycle for wallet {wallet} was cancelled.")
            break # Exit loop if task is cancelled
        except Exception as e:
            logging.error(f"Error in billion_cycle for wallet {wallet}: {e}", exc_info=True)
            # Decide on recovery strategy: break, continue, or retry with backoff
            await asyncio.sleep(10) # Wait before retrying or exiting to prevent rapid error loops
            # For now, let's break the loop on unhandled error after logging
            break

@app.get("/profit_events")
async def get_profits(wallet: str):
    return {"profitEvents": profit_events.get(wallet, [])}

@app.get("/status")
async def status():
    # Now returns individual scaling factors, or could be an average, etc.
    return {"wallets": wallets, "wallet_scaling_factors": wallet_scaling_factors, "profit_events": profit_events}

@app.post("/adjust_scaling_factor", summary="Manually adjust the scaling factor for a specific wallet.")
async def adjust_scaling_factor(req: AdjustScalingFactorRequest):
    """
    Allows manual adjustment of the scaling factor for a given wallet.
    This directly impacts the profit calculation in its active billion_cycle.
    """
    if req.wallet not in wallets:
        logging.warning(f"Attempted to adjust scaling factor for non-existent wallet: {req.wallet}")
        raise fastapi.HTTPException(status_code=404, detail=f"Wallet '{req.wallet}' not found.")

    if req.new_factor <= 0:
        logging.warning(f"Attempted to set invalid scaling factor for {req.wallet}: {req.new_factor}")
        raise fastapi.HTTPException(status_code=400, detail="Scaling factor must be a positive number.")

    old_factor = wallet_scaling_factors.get(req.wallet) # Should exist if wallet is in `wallets` list and was processed by collect_wallet
    if old_factor is None: # Should ideally not happen if wallet is in `wallets` list from collect_wallet
        logging.error(f"Wallet {req.wallet} found in wallets list but not in wallet_scaling_factors dict. This indicates a state inconsistency.")
        # Initialize it before setting, or handle as a server error
        wallet_scaling_factors[req.wallet] = 1.0 # Default initialization
        old_factor = 1.0
        logging.info(f"Initialized missing scaling factor for {req.wallet} to 1.0 before adjustment.")
    wallet_scaling_factors[req.wallet] = req.new_factor
    logging.info(f"Manually adjusted scaling factor for wallet {req.wallet} from {old_factor} to {req.new_factor}")

    # Note: This changes the scaling factor used in the *next* iteration of its billion_cycle.
    # The currently running profit calculation (if any) for that wallet will use the factor it started with for that iteration.
    return {"status": "success", "wallet": req.wallet, "new_scaling_factor": req.new_factor}
