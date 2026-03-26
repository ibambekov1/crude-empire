"""
Price fetcher for live WTI Crude and Henry Hub Natural Gas prices.
Falls back to simulated prices if APIs are unavailable.
"""

import random
import math
import os
from datetime import datetime

# Default prices if live fetch fails
DEFAULT_WTI = 70.0
DEFAULT_GAS = 3.50


def fetch_live_prices() -> dict:
    """
    Attempt to fetch live WTI and Henry Hub prices.
    Uses Yahoo Finance API via yfinance if available,
    otherwise falls back to simulated prices.
    """
    try:
        import yfinance as yf

        # CL=F is WTI Crude Oil Futures
        # NG=F is Henry Hub Natural Gas Futures
        oil = yf.Ticker("CL=F")
        gas = yf.Ticker("NG=F")

        oil_hist = oil.history(period="1d")
        gas_hist = gas.history(period="1d")

        wti = float(oil_hist["Close"].iloc[-1]) if not oil_hist.empty else DEFAULT_WTI
        ng = float(gas_hist["Close"].iloc[-1]) if not gas_hist.empty else DEFAULT_GAS

        return {
            "wti": round(wti, 2),
            "gas": round(ng, 2),
            "source": "Yahoo Finance (Live)",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "wti": DEFAULT_WTI,
            "gas": DEFAULT_GAS,
            "source": f"Default (API unavailable: {str(e)[:50]})",
            "timestamp": datetime.now().isoformat(),
        }


def simulate_price_movement(current_price: float, volatility: float = 0.08,
                            mean_reversion: float = 0.02,
                            long_term_mean: float = None) -> float:
    """
    Simulate monthly price movement using mean-reverting GBM.
    Good for game simulation when live prices aren't available.
    """
    if long_term_mean is None:
        long_term_mean = current_price

    dt = 1 / 12  # Monthly
    drift = mean_reversion * (math.log(long_term_mean) - math.log(current_price)) * dt
    shock = volatility * math.sqrt(dt) * random.gauss(0, 1)
    new_price = current_price * math.exp(drift + shock)

    return round(max(new_price, current_price * 0.5), 2)  # Floor at 50% drop in one month


def simulate_wti(current: float) -> float:
    return simulate_price_movement(current, volatility=0.25, mean_reversion=0.15, long_term_mean=72.0)


def simulate_gas(current: float) -> float:
    return simulate_price_movement(current, volatility=0.35, mean_reversion=0.20, long_term_mean=3.50)
