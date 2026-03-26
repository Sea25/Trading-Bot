from flask import Flask, render_template_string, request, jsonify
import os
from dotenv import load_dotenv
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import place_order

load_dotenv()
logger = setup_logging()

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Trading Bot — Binance Testnet</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg: #0a0c10;
    --panel: #10141c;
    --border: #1e2530;
    --accent: #00e5ff;
    --accent2: #ff4560;
    --green: #00e096;
    --text: #cdd6f4;
    --muted: #555e78;
    --font-mono: 'Share Tech Mono', monospace;
    --font-sans: 'Syne', sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-sans);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 16px;
  }
  header { text-align: center; margin-bottom: 40px; }
  header h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; color: #fff; }
  header h1 span { color: var(--accent); }
  header p { font-family: var(--font-mono); color: var(--muted); font-size: 0.8rem; margin-top: 6px; letter-spacing: 2px; text-transform: uppercase; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 32px; width: 100%; max-width: 520px; box-shadow: 0 0 60px rgba(0,229,255,0.04); }
  .field { margin-bottom: 20px; }
  label { display: block; font-family: var(--font-mono); font-size: 0.72rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
  input, select { width: 100%; background: #0d1117; border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-family: var(--font-mono); font-size: 0.95rem; padding: 11px 14px; outline: none; transition: border-color .2s; }
  input:focus, select:focus { border-color: var(--accent); }
  select option { background: #0d1117; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  #price-row { transition: opacity .3s; }
  #price-row.hidden { opacity: 0.2; pointer-events: none; }
  #stop-row { transition: opacity .3s; }
  #stop-row.hidden { opacity: 0.2; pointer-events: none; }
  .side-toggle { display: flex; gap: 10px; }
  .side-toggle button { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid var(--border); background: transparent; color: var(--muted); font-family: var(--font-mono); font-size: 0.9rem; cursor: pointer; transition: all .2s; letter-spacing: 1px; }
  .side-toggle button.buy.active  { background: rgba(0,224,150,.15); border-color: var(--green); color: var(--green); }
  .side-toggle button.sell.active { background: rgba(255,69,96,.15);  border-color: var(--accent2); color: var(--accent2); }
  #side-input { display: none; }
  .submit-btn { width: 100%; padding: 14px; background: var(--accent); color: #000; font-family: var(--font-sans); font-weight: 700; font-size: 1rem; border: none; border-radius: 10px; cursor: pointer; letter-spacing: 1px; transition: opacity .2s, transform .1s; margin-top: 8px; }
  .submit-btn:hover { opacity: .88; }
  .submit-btn:active { transform: scale(.98); }
  .submit-btn:disabled { opacity: .4; cursor: not-allowed; }
  #result { margin-top: 24px; background: #0d1117; border: 1px solid var(--border); border-radius: 10px; padding: 20px; font-family: var(--font-mono); font-size: 0.82rem; line-height: 1.8; display: none; }
  #result.success { border-color: var(--green); }
  #result.error   { border-color: var(--accent2); }
  .tag { display: inline-block; font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; letter-spacing: 1px; font-weight: 700; margin-bottom: 10px; }
  .tag.success { background: rgba(0,224,150,.15); color: var(--green); }
  .tag.error   { background: rgba(255,69,96,.15);  color: var(--accent2); }
  .result-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #1a1f2e; }
  .result-row:last-child { border-bottom: none; }
  .result-key { color: var(--muted); }
  .result-val { color: var(--text); }
  .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(0,0,0,.3); border-top-color: #000; border-radius: 50%; animation: spin .6s linear infinite; vertical-align: middle; margin-right: 6px; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<header>
  <h1>Futures <span>TestNet</span> Bot</h1>
  <p>Binance USDT-M · REST API</p>
</header>
<div class="card">
  <div class="field">
    <label>Side</label>
    <div class="side-toggle">
      <button type="button" class="buy active" onclick="setSide('BUY',this)">▲ BUY</button>
      <button type="button" class="sell"       onclick="setSide('SELL',this)">▼ SELL</button>
    </div>
    <input type="hidden" id="side-input" value="BUY"/>
  </div>
  <div class="row">
    <div class="field">
      <label>Symbol</label>
      <input id="symbol" type="text" value="BTCUSDT" placeholder="BTCUSDT"/>
    </div>
    <div class="field">
      <label>Order Type</label>
      <select id="order-type" onchange="onTypeChange()">
        <option value="MARKET">MARKET</option>
        <option value="LIMIT">LIMIT</option>
        <option value="STOP_MARKET">STOP_MARKET</option>
      </select>
    </div>
  </div>
  <div class="field">
    <label>Quantity</label>
    <input id="quantity" type="number" step="any" placeholder="0.002"/>
  </div>
  <div class="field" id="price-row">
    <label>Limit Price (USDT)</label>
    <input id="price" type="number" step="any" placeholder="e.g. 90000"/>
  </div>
  <div class="field hidden" id="stop-row">
    <label>Stop Price (USDT)</label>
    <input id="stop-price" type="number" step="any" placeholder="e.g. 80000"/>
  </div>
  <button class="submit-btn" id="submit-btn" onclick="submitOrder()">Place Order</button>
  <div id="result"></div>
</div>
<script>
function setSide(val, el) {
  document.getElementById('side-input').value = val;
  document.querySelectorAll('.side-toggle button').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
}
function onTypeChange() {
  const t = document.getElementById('order-type').value;
  document.getElementById('price-row').classList.toggle('hidden', t !== 'LIMIT');
  document.getElementById('stop-row').classList.toggle('hidden', t !== 'STOP_MARKET');
}
async function submitOrder() {
  const btn = document.getElementById('submit-btn');
  const result = document.getElementById('result');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Placing...';
  result.style.display = 'none';
  const payload = {
    symbol:     document.getElementById('symbol').value.trim(),
    side:       document.getElementById('side-input').value,
    order_type: document.getElementById('order-type').value,
    quantity:   parseFloat(document.getElementById('quantity').value),
    price:      parseFloat(document.getElementById('price').value) || null,
    stop_price: parseFloat(document.getElementById('stop-price').value) || null,
  };
  try {
    const res = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      const r = data.response;
      result.className = 'success';
      result.innerHTML =
        '<div class="tag success">✓ ORDER PLACED</div>' +
        row('Order ID', r.orderId) + row('Status', r.status) +
        row('Symbol', r.symbol) + row('Side', r.side) +
        row('Type', r.type) + row('Executed Qty', r.executedQty) +
        row('Avg Price', r.avgPrice || 'N/A') + row('Client OID', r.clientOrderId);
    } else {
      result.className = 'error';
      result.innerHTML = '<div class="tag error">✗ FAILED</div><div style="color:var(--accent2)">' + data.error + '</div>';
    }
  } catch(e) {
    result.className = 'error';
    result.innerHTML = '<div class="tag error">✗ NETWORK ERROR</div><div style="color:var(--accent2)">' + e.message + '</div>';
  }
  result.style.display = 'block';
  btn.disabled = false;
  btn.innerHTML = 'Place Order';
}
function row(k, v) {
  return '<div class="result-row"><span class="result-key">' + k + '</span><span class="result-val">' + v + '</span></div>';
}
onTypeChange();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/order", methods=["POST"])
def api_order():
    data = request.json
    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        return jsonify({"success": False, "error": "API credentials not configured in .env"})
    try:
        client = BinanceClient(api_key, api_secret)
        response = place_order(
            client,
            symbol=data["symbol"],
            side=data["side"],
            order_type=data["order_type"],
            quantity=float(data["quantity"]),
            price=data.get("price"),
            stop_price=data.get("stop_price")
        )
        return jsonify({"success": True, "response": response})
    except (ValueError, RuntimeError) as e:
        logger.error(f"UI order error: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)