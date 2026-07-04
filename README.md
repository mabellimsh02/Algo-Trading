# Algo-Trading

A small moving-average crossover trading bot built around free market data (`yfinance`), vectorized backtesting (`vectorbt`), and Alpaca's **paper trading** API. It can backtest the strategy on historical data or run it against a live paper-trading account — no real money is involved.

## Strategy

The bot trades a classic golden-cross / death-cross moving-average strategy:

- **Entry (long):** the fast SMA crosses above the slow SMA (golden cross)
- - **Exit:** the fast SMA crosses below the slow SMA (death cross), or a stop-loss/take-profit level is hit
  - - Position size is risk-based: each trade risks a fixed percentage of account equity, calculated from the stop-loss distance
   
    - Defaults are a 50/200-day crossover, 1% stop-loss, 3% take-profit, and 2% equity risk per trade — all configurable via environment variables.
   
    - ## Files
   
    - - `algobot.py` — CLI entry point (`backtest` and `trade` subcommands)
      - - `data_fetcher.py` — downloads historical OHLCV data via yfinance
        - - `strategy.py` — computes moving averages and generates entry/exit signals
          - - `backtester.py` — runs a vectorbt backtest over the signals and reports return, win rate, Sharpe ratio, drawdown, etc.
            - - `paper_trader.py` — connects to Alpaca's paper trading API, sizes positions, and submits bracket orders (entry + stop-loss + take-profit) based on today's signal
              - - `trade_logger.py` — logs bot activity and appends every executed trade to a CSV
                - - `config.py` — central configuration, loaded from environment variables / `.env`
                  - - `.env.example` — template for the environment variables the bot needs
                   
                    - ## Requirements
                   
                    - - Python 3.10+
                      - - Packages listed in `requirements.txt`: yfinance, vectorbt, numba, llvmlite, alpaca-trade-api, pandas, numpy, python-dotenv
                       
                        - Install with:
                       
                        - ```bash
                          pip install -r requirements.txt
                          ```

                          ## Setup

                          1. Create a free Alpaca account and generate **paper trading** API keys at the [Alpaca paper dashboard](https://app.alpaca.markets/paper/dashboard/overview).
                          2. 2. Copy `.env.example` to `.env` and fill in `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`. Leave `ALPACA_BASE_URL` pointed at the paper-api endpoint.
                             3. 3. Optionally override strategy, backtest, or risk parameters in the same `.env` file.
                               
                                4. ## Usage
                               
                                5. Backtest a ticker over historical data:
                               
                                6. ```bash
                                   python algobot.py backtest AAPL --period 5y
                                   ```

                                   Check today's signal and place a paper trade (intended to run once, near market open):

                                   ```bash
                                   python algobot.py trade AAPL MSFT
                                   ```

                                   Trade logs are written to `logs/trades.csv` and `logs/bot.log`.

                                   ## Disclaimer

                                   This project only trades against Alpaca's **paper trading** environment (simulated money) and is meant for learning about strategy backtesting and automation, not as financial advice or a system for trading real funds.
