#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hmac
import hashlib
import base64
import time
import json
import requests
from datetime import datetime, timezone
from typing import Dict, Optional, Any, Tuple

from telemetry import log_info, log_error, log_warning, log_debug

class OKXExchange:
    def __init__(self, api_key: str, secret_key: str, passphrase: str, demo: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.demo = demo
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self._connected = False
        self._time_offset = 0
        self._instrument_cache = {}
        log_info("Exchange", "Instancia creada", {"demo": demo})

    # ---------- AUTENTICACIÓN ----------
    def _get_server_timestamp_iso(self) -> Tuple[str, int]:
        try:
            resp = self.session.get(f"{self.base_url}/api/v5/public/time", timeout=5)
            data = resp.json()
            if data.get('code') != '0':
                raise Exception(f"Error obteniendo timestamp: {data}")
            ts_ms = int(data['data'][0]['ts'])
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            iso = dt.strftime('%Y-%m-%dT%H:%M:%S.') + f"{ts_ms % 1000:03d}Z"
            return iso, ts_ms
        except Exception as e:
            log_error("Exchange", "Error obteniendo timestamp", {"error": str(e)})
            raise

    def _sign_request(self, timestamp_iso: str, method: str, request_path: str, body: str = '') -> str:
        message = timestamp_iso + method.upper() + request_path + body
        mac = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def _build_headers(self, method: str, request_path: str, body: str = '') -> Dict:
        timestamp_iso, _ = self._get_server_timestamp_iso()
        signature = self._sign_request(timestamp_iso, method, request_path, body)
        headers = {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp_iso,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
        }
        if self.demo:
            headers['x-simulated-trading'] = '1'
        return headers

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                 body: Optional[Dict] = None, retries: int = 3) -> Dict:
        url = self.base_url + endpoint
        body_str = json.dumps(body) if body else ''
        request_path = endpoint
        if params and method.upper() == 'GET':
            query = '&'.join([f"{k}={v}" for k, v in params.items()])
            request_path = endpoint + '?' + query

        for attempt in range(1, retries + 1):
            try:
                headers = self._build_headers(method, request_path, body_str)
                if method.upper() == 'GET':
                    resp = self.session.get(url, headers=headers, params=params, timeout=15)
                else:
                    resp = self.session.post(url, headers=headers, params=params, json=body, timeout=15)
                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}: {resp.text}")
                data = resp.json()
                if data.get('code') != '0':
                    raise Exception(f"API Error {data.get('code')}: {data.get('msg')}")
                log_debug("Exchange", "Request OK", {"endpoint": endpoint})
                return {'ok': True, 'data': data, 'error': None}
            except Exception as e:
                log_warning("Exchange", f"Request falló (intento {attempt}/{retries})",
                            {"endpoint": endpoint, "error": str(e)})
                if attempt == retries:
                    return {'ok': False, 'error': str(e), 'data': None}
                time.sleep(1 * (2 ** (attempt - 1)))
        return {'ok': False, 'error': 'Max retries exceeded', 'data': None}

    # ---------- CONEXIÓN Y BALANCE ----------
    def connect(self) -> bool:
        try:
            result = self._request('GET', '/api/v5/public/time', retries=2)
            if result.get('ok'):
                self._connected = True
                log_info("Exchange", "Conexión exitosa")
                return True
            return False
        except Exception as e:
            log_error("Exchange", "Conexión fallida", {"error": str(e)})
            return False

    def get_balance(self, currency: str = 'USDT') -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        result = self._request('GET', '/api/v5/account/balance')
        if not result.get('ok'):
            return result
        from models import Balance
        details = result['data'].get('data', [{}])[0].get('details', [])
        usdt = next((d for d in details if d.get('ccy') == currency), {})
        bal = Balance(
            total=float(usdt.get('eq', 0)),
            free=float(usdt.get('cashBal', 0)),
            frozen=float(usdt.get('frozenBal', 0))
        )
        return {'ok': True, 'data': bal, 'error': None}

    def get_positions(self, inst_id: Optional[str] = None) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        params = {'instId': inst_id} if inst_id else {}
        result = self._request('GET', '/api/v5/account/positions', params=params)
        if not result.get('ok'):
            return result
        from models import Position
        positions_data = result['data'].get('data', [])
        positions = []
        for p in positions_data:
            if abs(float(p.get('pos', 0))) > 0.0001:
                positions.append(Position(
                    symbol=p.get('instId', ''),
                    side='long' if float(p.get('pos', 0)) > 0 else 'short',
                    size=abs(float(p.get('pos', 0))),
                    entry_price=float(p.get('avgPx', 0)),
                    mark_price=float(p.get('markPx', 0)),
                    pnl=float(p.get('upl', 0)),
                    pnl_pct=float(p.get('uplRatio', 0)) * 100
                ))
        return {'ok': True, 'data': positions, 'error': None}

    # ---------- ÓRDENES ----------
    def place_market_order(self, inst_id: str, side: str, size: float, leverage: int = 10) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        self._request('POST', '/api/v5/account/set-leverage',
                      body={'instId': inst_id, 'lever': str(leverage), 'mgnMode': 'isolated'})
        body = {
            'instId': inst_id,
            'tdMode': 'isolated',
            'side': side,
            'ordType': 'market',
            'sz': str(size),
            'posSide': 'long' if side == 'buy' else 'short'
        }
        result = self._request('POST', '/api/v5/trade/order', body=body)
        if not result.get('ok'):
            return result
        from models import OrderResult
        order_data = result['data'].get('data', [{}])[0]
        return {'ok': True, 'data': OrderResult(ord_id=order_data.get('ordId', '')),
                'error': None}

    # ---------- ÓRDENES ALGORÍTMICAS (desde v2) ----------
    def place_algo_order(self, inst_id: str, side: str, size: float,
                         tp_price: Optional[float] = None,
                         sl_price: Optional[float] = None,
                         trail_callback: Optional[float] = None) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        if not tp_price and not sl_price and not trail_callback:
            return {'ok': False, 'error': 'Se requiere TP, SL o trailing', 'data': None}
        body = {
            'instId': inst_id,
            'tdMode': 'isolated',
            'side': side,
            'sz': str(size),
            'reduceOnly': True,
        }
        if trail_callback:
            body['ordType'] = 'move_order_stop'
            body['callbackRatio'] = str(trail_callback)
            body['triggerPxType'] = 'last'
        else:
            body['ordType'] = 'conditional'
            if tp_price:
                body['tpTriggerPx'] = str(tp_price)
                body['tpOrdPx'] = str(tp_price)
            if sl_price:
                body['slTriggerPx'] = str(sl_price)
                body['slOrdPx'] = str(sl_price)
        body['posSide'] = 'long' if side == 'sell' else 'short'
        result = self._request('POST', '/api/v5/trade/order-algo', body=body)
        if not result.get('ok'):
            return result
        from models import OrderResult
        algo_data = result['data'].get('data', [{}])[0]
        return {'ok': True, 'data': OrderResult(ord_id=algo_data.get('algoId', ''),
                                                algo_id=algo_data.get('algoId', '')),
                'error': None}

    def place_trailing_stop_order(self, inst_id: str, side: str, size: float,
                                  callback_ratio: float) -> Dict:
        return self.place_algo_order(inst_id, side, size, trail_callback=callback_ratio)

    def modify_algo_order(self, inst_id: str, algo_id: str,
                          tp_price: Optional[float] = None,
                          sl_price: Optional[float] = None) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        body = {'instId': inst_id, 'algoId': algo_id}
        if tp_price is not None:
            body['tpTriggerPx'] = str(tp_price)
            body['tpOrdPx'] = str(tp_price)
        if sl_price is not None:
            body['slTriggerPx'] = str(sl_price)
            body['slOrdPx'] = str(sl_price)
        return self._request('POST', '/api/v5/trade/amend-algos', body=body)

    def cancel_algo_order(self, inst_id: str, algo_id: str) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        return self._request('POST', '/api/v5/trade/cancel-algos',
                             body={'instId': inst_id, 'algoId': algo_id})

    def get_algo_order(self, inst_id: str, algo_id: str) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        result = self._request('GET', '/api/v5/trade/orders-algo-pending',
                               params={'instId': inst_id, 'algoId': algo_id})
        if result.get('ok'):
            data = result['data'].get('data', [])
            return {'ok': True, 'data': data[0] if data else None, 'error': None}
        return result

    def cancel_order(self, inst_id: str, ord_id: str) -> Dict:
        if not self._connected:
            return {'ok': False, 'error': 'No conectado', 'data': None}
        return self._request('POST', '/api/v5/trade/cancel-order',
                             body={'instId': inst_id, 'ordId': ord_id})