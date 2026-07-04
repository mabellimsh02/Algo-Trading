"""Trade logging: appends every executed trade to a CSV and sets up bot-wide logging."""
import csv
import logging
import os
from datetime import datetime, timezone

import config

TRADE_LOG_FIELDS = ["timestamp", "ticker", "action", "qty", "price", "pnl", "note"]


def setup_logging(level=logging.INFO) -> None:
    """Configure root logging to write to both console and a rotating-free log file."""
    os.makedirs(config.LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.BOT_LOG_FILE),
        ],
    )


def log_trade(ticker: str, action: str, price: float, qty: float = 0, pnl: float = None, note: str = "") -> None:
    """Append one trade record to the CSV trade log.

    action: "BUY" | "SELL" | "STOP_LOSS" | "TAKE_PROFIT"
    """
    os.makedirs(config.LOG_DIR, exist_ok=True)
    file_exists = os.path.isfile(config.TRADE_LOG_FILE)

    with open(config.TRADE_LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker,
            "action": action,
            "qty": qty,
            "price": price,
            "pnl": pnl if pnl is not None else "",
            "note": note,
        })

    logging.getLogger(__name__).info(
        "Trade logged: %s %s qty=%s price=%.2f pnl=%s", action, ticker, qty, price,
        f"{pnl:.2f}" if pnl is not None else "n/a"
    )
