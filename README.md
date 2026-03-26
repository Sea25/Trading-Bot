# Trading-Bot
Python trading bot that interacts with Binance Futures Testnet (a sandbox environment for testing futures trading without real money).


## Setup
```bash
git clone <your-repo>
cd trading_bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

Get credentials at: https://testnet.binancefuture.com

## CLI Usage
```bash
# Market BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

# Stop Market
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 60000
```

## Web UI (Bonus)
```bash
python ui.py
# Open http://localhost:5000
```

## Project Structure
```
trading_bot/
  bot/
    __init__.py
    client.py         # Binance REST client + signing
    orders.py         # Order placement + formatting
    validators.py     # Input validation
    logging_config.py # Rotating file + console logging
  cli.py              # argparse CLI entry point
  ui.py               # Flask Web UI (bonus)
  logs/               # Auto-created log files
  .env                # API credentials (not committed)
  requirements.txt
  README.md
```

## Assumptions

- Only USDT-M Futures Testnet is targeted
- `STOP_MARKET` is used as the bonus third order type
- Logs rotate at 5MB, keep 3 backups