"""Central configuration, loaded from environment variables (.env supported)."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Alpaca (paper trading) ---
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# --- Strategy parameters ---
FAST_MA = int(os.getenv("FAST_MA", 50))
SLOW_MA = int(os.getenv("SLOW_MA", 200))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.01))    # 1%
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.03))  # 3%

# --- Backtest defaults ---
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", 10_000))
COMMISSION_PCT = float(os.getenv("COMMISSION_PCT", 0.0))
DEFAULT_HISTORY_PERIOD = os.getenv("DEFAULT_HISTORY_PERIOD", "5y")

# --- Position sizing (paper trading) ---
RISK_PCT_PER_TRADE = float(os.getenv("RISK_PCT_PER_TRADE", 0.02))  # fraction of equity risked per trade

# --- Logging ---
LOG_DIR = os.getenv("LOG_DIR", "logs")
TRADE_LOG_FILE = os.path.join(LOG_DIR, "trades.csv")
BOT_LOG_FILE = os.path.join(LOG_DIR, "bot.log")
