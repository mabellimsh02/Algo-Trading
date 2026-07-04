"""Runs a vectorbt backtest over generated signals and reports key metrics."""
import logging

import pandas as pd
import vectorbt as vbt

import config

logger = logging.getLogger(__name__)


def run_backtest(
    df: pd.DataFrame,
    init_cash: float = None,
    fees: float = None,
    sl_stop: float = None,
    tp_stop: float = None,
) -> vbt.Portfolio:
    """Run a long-only backtest with a fixed stop-loss / take-profit per trade.

    df must contain a 'Close' column plus boolean 'entries' / 'exits' columns,
    as produced by strategy.generate_signals().
    """
    init_cash = init_cash if init_cash is not None else config.INITIAL_CAPITAL
    fees = fees if fees is not None else config.COMMISSION_PCT
    sl_stop = sl_stop if sl_stop is not None else config.STOP_LOSS_PCT
    tp_stop = tp_stop if tp_stop is not None else config.TAKE_PROFIT_PCT

    portfolio = vbt.Portfolio.from_signals(
        close=df["Close"],
        entries=df["entries"],
        exits=df["exits"],
        sl_stop=sl_stop,
        tp_stop=tp_stop,
        init_cash=init_cash,
        fees=fees,
        direction="longonly",
        freq="1D",
    )
    return portfolio


def print_metrics(portfolio: vbt.Portfolio, ticker: str = "") -> dict:
    """Print and return a dict of key backtest metrics."""
    trades = portfolio.trades

    total_return = portfolio.total_return()
    sharpe = portfolio.sharpe_ratio()
    max_dd = portfolio.max_drawdown()
    win_rate = trades.win_rate() if trades.count() > 0 else float("nan")
    n_trades = trades.count()

    metrics = {
        "ticker": ticker,
        "total_return_pct": total_return * 100,
        "win_rate_pct": win_rate * 100 if pd.notna(win_rate) else float("nan"),
        "sharpe_ratio": sharpe,
        "max_drawdown_pct": max_dd * 100,
        "num_trades": n_trades,
        "final_value": portfolio.final_value(),
    }

    header = f"Backtest results{f' for {ticker}' if ticker else ''}"
    print(f"\n{header}")
    print("-" * len(header))
    print(f"Total return:   {metrics['total_return_pct']:.2f}%")
    print(f"Win rate:       {metrics['win_rate_pct']:.2f}%")
    print(f"Sharpe ratio:   {metrics['sharpe_ratio']:.2f}")
    print(f"Max drawdown:   {metrics['max_drawdown_pct']:.2f}%")
    print(f"Number trades:  {metrics['num_trades']}")
    print(f"Final value:    ${metrics['final_value']:.2f} (from ${config.INITIAL_CAPITAL:.2f})")

    return metrics


if __name__ == "__main__":
    import sys

    from data_fetcher import fetch_ohlcv
    from strategy import generate_signals

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    data = fetch_ohlcv(ticker)
    signals = generate_signals(data)
    pf = run_backtest(signals)
    print_metrics(pf, ticker)
