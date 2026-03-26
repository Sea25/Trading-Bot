# Trading Bot — Binance Futures Testnet

A clean, structured Python CLI for placing orders on the **Binance Futures Testnet (USDT-M)** using raw REST calls.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance REST API client (signing, requests)
│   ├── orders.py            # Order placement logic + output formatting
│   ├── validators.py        # Input validation
│   └── logging_config.py   # Structured file + console logging
├── cli.py                   # CLI entry point (argparse)
├── logs/                    # Auto-created; contains trading_bot.log
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/Sea25/Trading-Bot.git
cd Trading-Bot
pip install -r requirements.txt
```

### 2. Get Binance Futures Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub or Google account
3. Navigate to **API Management** → generate an API key + secret

### 3. Set your credentials

**Option A — environment variables (recommended):**

```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

**Option B — pass as flags on every command:**

```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET <command>
```

---

## How to Run

### Place a MARKET order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01
```

### Place a LIMIT order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.01 \
  --price 50000
```

### Place a STOP_MARKET order (bonus order type)

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type STOP_MARKET \
  --quantity 0.01 \
  --stop-price 40000
```

### Check your account balances

```bash
python cli.py account
```

### List open orders

```bash
python cli.py open-orders --symbol BTCUSDT
```

---

## Sample Output

```
============================================================
  ORDER REQUEST SUMMARY
============================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
============================================================
  ORDER RESPONSE
============================================================
  Order ID      : 3951409639
  Client OID    : web_abc123
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Orig Qty      : 0.01
  Executed Qty  : 0.01
  Avg Price     : 67423.50
  Time In Force : GTC
============================================================
  ✓ Order placed successfully!
```

---

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

- **File log**: DEBUG level (verbose — full request params, raw responses)
- **Console log**: INFO level (clean, not noisy)

Log files from a MARKET and LIMIT order are included in the `logs/` folder.

---

## Assumptions

- All orders use the **USDT-M Futures Testnet** (`https://testnet.binancefuture.com`)
- Quantities and prices are passed as-is to the API; symbol precision rules are enforced by the exchange
- `timeInForce` defaults to `GTC` for LIMIT orders
- Credentials are never hardcoded — always passed via env vars or CLI flags

---

## Bonus Feature

**STOP_MARKET orders** are supported as a third order type:

```bash
python cli.py place-order --symbol ETHUSDT --side SELL --type STOP_MARKET --quantity 0.1 --stop-price 2800
```