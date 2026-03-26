import hashlib
import hmac
import time
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
        })

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _post(self, endpoint: str, params: dict) -> dict:
        signed_params = self._sign(params)
        url = f"{BASE_URL}{endpoint}"
        logger.debug(f"POST {url} | params: { {k: v for k, v in signed_params.items() if k != 'signature'} }")
        try:
            response = self.session.post(url, params=signed_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response: {data}")
            return data
        except requests.exceptions.HTTPError as e:
            try:
                error_body = e.response.json()
            except Exception:
                error_body = {"msg": e.response.text}
            logger.error(f"HTTP error: {e} | body: {error_body}")
            raise RuntimeError(f"API Error {error_body.get('code')}: {error_body.get('msg', str(e))}")
        except requests.exceptions.ConnectionError:
            logger.error("Network connection failed.")
            raise RuntimeError("Network error: Unable to reach Binance Testnet. Check your connection.")
        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise RuntimeError("Request timed out. Try again.")

    def _get(self, endpoint: str, params: dict = None) -> dict:
        params = params or {}
        signed_params = self._sign(params)
        url = f"{BASE_URL}{endpoint}"
        logger.debug(f"GET {url} | params: { {k: v for k, v in signed_params.items() if k != 'signature'} }")
        try:
            response = self.session.get(url, params=signed_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response: {data}")
            return data
        except requests.exceptions.HTTPError as e:
            try:
                error_body = e.response.json()
            except Exception:
                error_body = {"msg": e.response.text}
            logger.error(f"HTTP error: {e} | body: {error_body}")
            raise RuntimeError(f"API Error {error_body.get('code')}: {error_body.get('msg', str(e))}")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Network error: Unable to reach Binance Testnet.")
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out.")

    def place_order(self, params: dict) -> dict:
        return self._post("/fapi/v1/order", params)

    def get_account(self) -> dict:
        return self._get("/fapi/v2/account")

    def get_open_orders(self, symbol: str) -> list:
        return self._get("/fapi/v1/openOrders", {"symbol": symbol})