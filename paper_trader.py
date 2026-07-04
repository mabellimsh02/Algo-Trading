"""Connects to Alpaca paper trading and executes MA-crossover signals at market open.

Entries are submitted as bracket orders (stop-loss + take-profit attached),
so Alpaca manages the exit once a position is open. Death-cross exit signals
close any open position early.
"""
import logging

import alpaca_trade_api as tradeapi

import config
from data_fetcher import fetch_ohlcv
from strategy import generate_signals
from trade_logger import log_trade, setup_logging

logger = logging.getLogger(__name__)


def get_api() -> tradeapi.REST:
    if not config.ALPACA_API_KEY or not config.ALPACA_SECRET_KEY:
        raise RuntimeError(
            "Alpaca API credentials are missing. Set ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY (e.g. in a .env file)."
        )
    return tradeapi.REST(
        config.ALPACA_API_KEY,
        config.ALPACA_SECRET_KEY,
        config.ALPACA_BASE_URL,
        api_version="v2",
    )


def market_is_open(api: tradeapi.REST) -> bool:
    return api.get_clock().is_open


def get_open_position(api: tradeapi.REST, ticker: str):
    try:
        return api.get_position(ticker)
    except tradeapi.rest.APIError:
        return None


def calc_position_size(api: tradeapi.REST, price: float, stop_loss_pct: float) -> int:
    """Size the position so that hitting the stop loss risks RISK_PCT_PER_TRADE of equity."""
    account = api.get_account()
    equity = float(account.equity)
    risk_amount = equity * config.RISK_PCT_PER_TRADE
    per_share_risk = price * stop_loss_pct
    if per_share_risk <= 0:
        return 0
    qty = int(risk_amount / per_share_risk)
    return max(qty, 0)


def submit_entry(api: tradeapi.REST, ticker: str, price: float) -> None:
    qty = calc_position_size(api, price, config.STOP_LOSS_PCT)
    if qty <= 0:
        logger.warning("Calculated position size for %s is 0; skipping entry.", ticker)
        return

    stop_price = round(price * (1 - config.STOP_LOSS_PCT), 2)
    take_profit_price = round(price * (1 + config.TAKE_PROFIT_PCT), 2)

    order = api.submit_order(
        symbol=ticker,
        qty=qty,
        side="buy",
        type="market",
        time_in_force="day",
        order_class="bracket",
        take_profit={"limit_price": take_profit_price},
        stop_loss={"stop_price": stop_price},
    )
    logger.info(
        "Submitted BUY bracket order for %s: qty=%d entry~%.2f sl=%.2f tp=%.2f",
        ticker, qty, price, stop_price, take_profit_price,
    )
    log_trade(ticker, "BUY", price, qty=qty, note=f"sl={stop_price} tp={take_profit_price} order_id={order.id}")


def submit_exit(api: tradeapi.REST, ticker: str, price: float, position) -> None:
    qty = abs(float(position.qty))
    order = api.close_position(ticker)
    unrealized_pnl = float(position.unrealized_pl)
    logger.info("Submitted SELL to close %s: qty=%s price~%.2f pnl~%.2f", ticker, qty, price, unrealized_pnl)
    log_trade(ticker, "SELL", price, qty=qty, pnl=unrealized_pnl, note=f"death_cross order_id={order.id}")


def run_once(ticker: str) -> None:
    """Check today's signal for a ticker and act on it. Intended to run once, near market open."""
    api = get_api()

    if not market_is_open(api):
        logger.info("Market is closed; no action taken for %s.", ticker)
        return

    data = fetch_ohlcv(ticker, period="1y")
    signals = generate_signals(data)
    last = signals.iloc[-1]
    price = float(last["Close"])

    position = get_open_position(api, ticker)

    if last["entries"] and position is None:
        submit_entry(api, ticker, price)
    elif last["exits"] and position is not None:
        submit_exit(api, ticker, price, position)
    else:
        logger.info("No action for %s (entry=%s exit=%s has_position=%s)",
                    ticker, bool(last["entries"]), bool(last["exits"]), position is not None)


if __name__ == "__main__":
    import sys

    setup_logging()
    tickers = sys.argv[1:] or ["AAPL"]
    for t in tickers:
        run_once(t)
