import asyncio
import random
import logging # Added
import os # Added
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

import fastapi # Added for HTTPException
from enum import Enum # Added for StrategyName

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Strategy Definitions ---

class StrategyName(str, Enum):
    """Enum for predefined strategy names."""
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"

class StrategyConfig(BaseModel):
    """Configuration model for a trading strategy."""
    name: StrategyName
    min_profit_factor: float # e.g., 0.01 for 1% base profit relative to base_profit_amount
    max_profit_factor: float # e.g., 0.05 for 5% base profit relative to base_profit_amount
    risk_multiplier: float   # Placeholder for now, could affect profit volatility or (later) loss chance.
    base_profit_amount: float # Base amount used in profit calculation before factors and scaling.

PREDEFINED_STRATEGIES: Dict[StrategyName, StrategyConfig] = {
    StrategyName.LOW_RISK: StrategyConfig(
        name=StrategyName.LOW_RISK,
        min_profit_factor=0.005, # 0.5%
        max_profit_factor=0.02,  # 2%
        risk_multiplier=0.8,
        base_profit_amount=100_000
    ),
    StrategyName.MEDIUM_RISK: StrategyConfig(
        name=StrategyName.MEDIUM_RISK,
        min_profit_factor=0.01, # 1%
        max_profit_factor=0.05, # 5%
        risk_multiplier=1.0,
        base_profit_amount=150_000 # Slightly higher base for medium risk
    ),
    StrategyName.HIGH_RISK: StrategyConfig(
        name=StrategyName.HIGH_RISK,
        min_profit_factor=0.02,  # 2%
        max_profit_factor=0.10,  # 10%
        risk_multiplier=1.5,
        base_profit_amount=200_000 # Higher base for high risk
    ),
}

DEFAULT_STRATEGY_NAME = StrategyName.MEDIUM_RISK

# --- End Strategy Definitions ---

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Phantom AI Billion Dollar Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for simplicity. In a real application, use a database.
wallets: List[str] = [] # Stores registered wallet addresses
profit_events: Dict[str, List[Dict]] = {} # Stores simulated profit events per wallet
wallet_scaling_factors: Dict[str, float] = {} # Stores current scaling factor per wallet
wallet_strategies: Dict[str, StrategyName] = {} # Stores current strategy for each wallet

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
    Registers a new wallet if not already present. New wallets are randomly assigned a trading strategy.
    Initiates its autonomous profit generation cycle. Each wallet operates independently.
    Returns the registration status, wallet name, and assigned strategy.
    """
    if req.wallet not in wallets:
        wallets.append(req.wallet)
        wallet_scaling_factors[req.wallet] = 1.0 # Initialize scaling factor

        # Randomly assign a strategy to new wallets
        available_strategy_names = list(PREDEFINED_STRATEGIES.keys())
        assigned_strategy_name = random.choice(available_strategy_names)
        wallet_strategies[req.wallet] = assigned_strategy_name

        logging.info(f"Wallet {req.wallet} registered with randomly assigned strategy: {assigned_strategy_name}. Starting billion cycle.")
        asyncio.create_task(billion_cycle(wallet=req.wallet,
                                          initial_scaling_factor=1.0,
                                          strategy_name=assigned_strategy_name))
    else:
        # If wallet already exists, log its current strategy and don't change it.
        existing_strategy = wallet_strategies.get(req.wallet, "N/A (should not happen if registered)")
        logging.info(f"Wallet {req.wallet} already registered. Current strategy: {existing_strategy}")

    # Return the (newly assigned or existing) strategy in the response
    return {"status": "registered", "wallet": req.wallet, "strategy": wallet_strategies.get(req.wallet)}

async def billion_cycle(wallet: str, initial_scaling_factor: float, strategy_name: StrategyName):
    """
    Main asynchronous loop for a single wallet. Simulates profit generation based on an
    assigned strategy, sends profits (simulated), and handles scaling operations.
    Includes logic for dynamic strategy adaptation if a wallet fails to make
    significant progress over several cycles.
    """
    # global scaling_factor # Removed
    current_scaling_factor = initial_scaling_factor
    clone_count = 0

    try:
        strategy_config = PREDEFINED_STRATEGIES[strategy_name]
    except KeyError:
        logging.error(f"Invalid strategy_name '{strategy_name}' for wallet {wallet}. Falling back to default strategy.")
        strategy_name = DEFAULT_STRATEGY_NAME # Ensure strategy_name var is also updated
        strategy_config = PREDEFINED_STRATEGIES[strategy_name]
        wallet_strategies[wallet] = strategy_name # Correct the state if it was somehow invalid

    # State variables for dynamic strategy adaptation
    cycles_without_significant_progress: int = 0
    last_progress_check_weekly_total: float = 0.0
    # Constants for adaptation logic (could be made configurable later)
    ADAPTATION_THRESHOLD_CYCLES: int = 5
    MIN_SIGNIFICANT_PROGRESS_PERCENTAGE_OF_EXPECTED_PROFIT: float = 0.05 # 5%
    MAX_WEEKLY_TOTAL_ADAPTATION_FACTOR: float = 0.25 # Consider adaptation if weekly total < 25% of billion_target


    try:
        billion_target_str = os.environ.get("BILLION_TARGET_AMOUNT", "1000000000")
        billion_target = int(billion_target_str)
    except ValueError:
        logging.error(f"Invalid BILLION_TARGET_AMOUNT: {os.environ.get('BILLION_TARGET_AMOUNT')}. Using default 1,000,000,000.")
        billion_target = 1_000_000_000
    weekly_total = 0
    logging.info(f"Starting billion_cycle for wallet: {wallet} with strategy: {strategy_name}, initial_scaling_factor: {initial_scaling_factor}, Target: {billion_target}")

    while True:
        try:
            # 1. Simulate compounding trading/farming (risk and volume increase over time)
            await asyncio.sleep(random.randint(2, 5)) # Simulate time for trading/farming

            # Profit calculation using strategy config
            profit_this_cycle = random.uniform(strategy_config.min_profit_factor, strategy_config.max_profit_factor)
            profit_amount = round(profit_this_cycle * strategy_config.base_profit_amount * current_scaling_factor, 2)

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

            # --- Dynamic Strategy Adaptation Check ---
            # Consider adaptation only if not too close to the target
            if weekly_total < billion_target * MAX_WEEKLY_TOTAL_ADAPTATION_FACTOR:
                # Calculate expected profit for one cycle with current strategy and scale
                avg_strat_factor = (strategy_config.min_profit_factor + strategy_config.max_profit_factor) / 2
                expected_current_cycle_profit = strategy_config.base_profit_amount * avg_strat_factor * current_scaling_factor

                progress_this_period = weekly_total - last_progress_check_weekly_total
                significant_progress_threshold_value = expected_current_cycle_profit * MIN_SIGNIFICANT_PROGRESS_PERCENTAGE_OF_EXPECTED_PROFIT

                if progress_this_period >= significant_progress_threshold_value:
                    logging.debug(f"Wallet {wallet} (Strat: {strategy_name}): Significant progress made. Weekly total: {weekly_total}")
                    cycles_without_significant_progress = 0
                    last_progress_check_weekly_total = weekly_total
                else:
                    cycles_without_significant_progress += 1
                    logging.info(f"Wallet {wallet} (Strat: {strategy_name}): No significant progress. Cycle {cycles_without_significant_progress}/{ADAPTATION_THRESHOLD_CYCLES}. Weekly total: {weekly_total}")

                if cycles_without_significant_progress >= ADAPTATION_THRESHOLD_CYCLES:
                    logging.warning(f"Wallet {wallet} (Strat: {strategy_name}): Triggering strategy adaptation after {cycles_without_significant_progress} cycles of no significant progress.")

                    available_new_strategies = [s_name for s_name in PREDEFINED_STRATEGIES.keys() if s_name != strategy_name]
                    if not available_new_strategies: # Should not happen if more than one strategy exists
                        available_new_strategies = list(PREDEFINED_STRATEGIES.keys()) # Fallback to any strategy

                    if available_new_strategies: # Ensure there's something to switch to
                        new_strategy_name = random.choice(available_new_strategies)
                        strategy_name = new_strategy_name # Update local var for current cycle
                        strategy_config = PREDEFINED_STRATEGIES[new_strategy_name]
                        wallet_strategies[wallet] = new_strategy_name # Update global state

                        logging.warning(f"Wallet {wallet}: Adapted! Switched to strategy: {new_strategy_name}. Scaling factor {current_scaling_factor} maintained.")
                        cycles_without_significant_progress = 0 # Reset for new strategy
                        last_progress_check_weekly_total = weekly_total # Reset for new strategy
                    else:
                        logging.error(f"Wallet {wallet} (Strat: {strategy_name}): Could not find a new strategy to adapt to. This should not happen.")

            else: # weekly_total is high enough, no need to adapt strategy
                if cycles_without_significant_progress > 0 : # Reset if it was counting
                    logging.debug(f"Wallet {wallet} (Strat: {strategy_name}): Progress is good / nearing target, resetting adaptation counter.")
                    cycles_without_significant_progress = 0
                    last_progress_check_weekly_total = weekly_total


            # 3. Aggressive scaling: clone, double, and recurse
            if weekly_total < billion_target:
                current_scaling_factor *= 2
                wallet_scaling_factors[wallet] = current_scaling_factor # Update status dict
                logging.info(f"Wallet {wallet}: Scaling factor doubled to {current_scaling_factor}")

                clone_wallet = f"{wallet}_clone_{clone_count+1}"
                if clone_wallet not in wallets:
                    logging.info(f"Wallet {wallet}: Cloning to {clone_wallet} with strategy {strategy_name} and scaling factor {current_scaling_factor}")
                    wallets.append(clone_wallet)
                    wallet_scaling_factors[clone_wallet] = current_scaling_factor # Initialize for new clone
                    wallet_strategies[clone_wallet] = strategy_name # Clone inherits strategy
                    asyncio.create_task(billion_cycle(wallet=clone_wallet,
                                                      initial_scaling_factor=current_scaling_factor,
                                                      strategy_name=strategy_name))
                    clone_count += 1
            else:
                logging.info(f"Wallet {wallet} (Strategy: {strategy_name}): 🎉 Reached $1B target this week! Resetting weekly total and scaling factor.")
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

@app.get("/status", summary="Get the overall system status.")
async def status():
    """
    Returns a snapshot of the system's current state, including all registered wallets,
    their profit events, current scaling factors, and assigned strategies.
    """
    return {
        "wallets": wallets,
        "wallet_scaling_factors": wallet_scaling_factors,
        "profit_events": profit_events,
        "wallet_strategies": wallet_strategies # Added wallet strategies
    }

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
