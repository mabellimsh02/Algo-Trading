"""Moving-average crossover strategy: calculates MAs and generates long-only signals."""
import logging

import pandas as pd

import config

logger = logging.getLogger(__name__)


def add_moving_averages(df: pd.DataFrame, fast: int = None, slow: int = None) -> pd.DataFrame:
    """Attach fast/slow simple moving average columns to a copy of df."""
    fast = fast or config.FAST_MA
    slow = slow or config.SLOW_MA

    out = df.copy()
    out[f"MA_{fast}"] = out["Close"].rolling(window=fast).mean()
    out[f"MA_{slow}"] = out["Close"].rolling(window=slow).mean()
    return out


def generate_signals(df: pd.DataFrame, fast: int = None, slow: int = None) -> pd.DataFrame:
    """Generate golden-cross / death-cross entry & exit signals.

    Returns df with MA columns plus:
      entries - True on the bar the fast MA crosses above the slow MA (Golden Cross)
      exits   - True on the bar the fast MA crosses below the slow MA (Death Cross)
    """
    fast = fast or config.FAST_MA
    slow = slow or config.SLOW_MA

    out = add_moving_averages(df, fast, slow)
    fast_col, slow_col = f"MA_{fast}", f"MA_{slow}"

    above = out[fast_col] > out[slow_col]
    prev_above = above.shift(1)

    out["entries"] = above & ~prev_above.astype("boolean").fillna(False)
    out["exits"] = ~above & prev_above.astype("boolean").fillna(False)

    # No signal before the slow MA has enough data to be defined.
    warmup = out[slow_col].isna()
    out.loc[warmup, ["entries", "exits"]] = False

    n_entries = int(out["entries"].sum())
    n_exits = int(out["exits"].sum())
    logger.info("Generated %d entry signal(s) and %d exit signal(s)", n_entries, n_exits)
    return out


if __name__ == "__main__":
    import sys

    from data_fetcher import fetch_ohlcv

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    data = fetch_ohlcv(ticker)
    signals = generate_signals(data)
    print(signals[signals["entries"] | signals["exits"]].tail(10))
