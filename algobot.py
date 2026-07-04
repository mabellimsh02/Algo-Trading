"""CLI entry point for the algo trading bot.

Usage:
    python algobot.py backtest TICKER [--period 5y]
    python algobot.py trade TICKER [TICKER ...]
"""
import argparse
import logging

from trade_logger import setup_logging

logger = logging.getLogger(__name__)


def cmd_backtest(args) -> None:
    from data_fetcher import fetch_ohlcv
    from strategy import generate_signals
    from backtester import run_backtest, print_metrics

    data = fetch_ohlcv(args.ticker, period=args.period)
    signals = generate_signals(data)
    portfolio = run_backtest(signals)
    print_metrics(portfolio, args.ticker)


def cmd_trade(args) -> None:
    from paper_trader import run_once

    for ticker in args.tickers:
        run_once(ticker)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple MA crossover algo trading bot")
    sub = parser.add_subparsers(dest="command", required=True)

    bt = sub.add_parser("backtest", help="Backtest the MA crossover strategy on a ticker")
    bt.add_argument("ticker")
    bt.add_argument("--period", default=None, help="yfinance history period, e.g. 5y, 2y, max")
    bt.set_defaults(func=cmd_backtest)

    tr = sub.add_parser("trade", help="Check signals and execute paper trades via Alpaca")
    tr.add_argument("tickers", nargs="+")
    tr.set_defaults(func=cmd_trade)

    return parser


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
