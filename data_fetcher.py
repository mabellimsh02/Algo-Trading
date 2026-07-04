"""Pulls historical daily OHLCV data for a ticker via yfinance."""
import logging

import pandas as pd
import yfinance as yf

import config

logger = logging.getLogger(__name__)


def fetch_ohlcv(ticker: str, period: str = None, interval: str = "1d") -> pd.DataFrame:
    """Download daily OHLCV history for a single ticker.

    Returns a DataFrame indexed by date with columns:
    Open, High, Low, Close, Volume
    """
    period = period or config.DEFAULT_HISTORY_PERIOD
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    # yfinance returns a MultiIndex column when given extra kwargs in some versions;
    # flatten it so downstream code can rely on plain column names.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.index.name = "Date"
    logger.info("Fetched %d rows of %s data for %s", len(df), interval, ticker)
    return df


if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    data = fetch_ohlcv(ticker)
    print(data.tail())
