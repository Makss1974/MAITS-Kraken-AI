import os
import json
import gc
from datetime import datetime, timedelta

class MessageConstructor:
    """Генерує детальні звіти для UX та AI Guardian"""
    @staticmethod
    def create_report(level, trigger_data, action_taken, target_haven, risk_score):
        timestamp = datetime.now().strftime("%H:%M:%S")
        headers = {
            1: "⚠️ [ASSET SPECIFIC CRASH]",
            2: "🚨 [SYSTEMIC MARKET CRASH]",
            3: "🆘 [GLOBAL FINANCIAL COLLAPSE]"
        }
        
        header = headers.get(level, "📢 [MONITORING]")
        
        logic_map = {
            1: f"Актив {trigger_data.get('asset')} впав на {trigger_data.get('change')}% при стабільному BTC.",
            2: f"Системна паніка: BTC впав на {trigger_data.get('btc_change')}%. Ризик-індекс: {risk_score}/100.",
            3: f"Критичний депег USDT ({trigger_data.get('usdt_price')}) або обвал DXY. Глобальна загроза."
        }

        report = (
            f"{header}\n"
            f"⏰ Час: {timestamp} | Risk Score: {risk_score}/100\n"
            f"🧐 Аналіз: {logic_map.get(level)}\n"
            f"⚡ Дія: {action_taken}\n"
            f"⚓ Гавань: {target_haven}\n"
            f"__________________________________\n"
            f"🤖 MAITS Anti-Crash Unit v3.0"
        )
        return report

class AntiCrashEngine:
    def __init__(self):
        self.emergency_mode = False
        self.lock_until = {} 
        self.risk_level = 0
        self.log_path = "/home/ubuntu/03.KRAKEN_PROD/MAITS/state/trades_history.lsonl"
        
        self.safe_havens = {
            "HARD": ["PAXG", "XAUT"],        # Золото
            "ANTI_DXY": ["CHF", "JPY"],      # Валюти
            "FIAT": ["USD", "EUR"],          # Кеш
            "RESERVE": ["BTC"]               # Цифровий резерв
        }

    def analyze_and_run(self, market_data, macro_data, news_feed, active_positions):
        """Головний цикл захисту, що викликається з main.py"""
        self.risk_level = 0
        alerts = self._scan_threats(market_data, macro_data, news_feed)
        
        if not alerts:
            return None

        # Беремо найбільш критичну загрозу
        alert = alerts[0] 
        level = alert['level']
        route = self._determine_route(macro_data)
        action_desc = self._get_action_description(level, route)
        
        report = MessageConstructor.create_report(
            level=level,
            trigger_data=alert.get('data', {}),
            action_taken=action_desc,
            target_haven=route,
            risk_score=self.risk_level
        )
        
        # Логуємо для AI Guardian (Rule: Silent Operator)
        self._log_emergency(level, alert, action_desc, route)
        
        # Технічне виконання
        self._execute_technical_orders(level, alert, route, active_positions)
        
        return report

    def _scan_threats(self, market_data, macro_data, news_feed):
        alerts = []
        # Отримуємо зміну BTC з даних Сканнера
        btc_data = market_data.get('XBTUSD') or market_data.get('BTCUSD') or {}
        btc_change = btc_data.get('change_24h', 0)
        
        # Рівень 3: Глобальний депег або крах DXY
        usdt_price = market_data.get('USDT', {}).get('price', 1.0)
        if usdt_price < 0.96 or macro_data.get('dxy_crash', False):
            self.risk_level = 100
            alerts.append({'level': 3, 'data': {'usdt_price': usdt_price}})
            return alerts

        # Рівень 2: Паніка на всьому ринку
        panic_keywords = ["hack", "sec", "ban", "depeg", "liquidation"]
        panic_news = any(word in n.lower() for n in news_feed for word in panic_keywords)
        if btc_change <= -10.0 or panic_news:
            self.risk_level = 75
            alerts.append({'level': 2, 'data': {'btc_change': btc_change}})

        # Рівень 1: Локальний крах конкретного щиткоїна
        for asset, data in market_data.items():
            if "XBT" not in asset and data.get('change_24h', 0) <= -12.0 and btc_change > -4.0:
                if asset not in self.lock_until:
                    alerts.append({'level': 1, 'data': {'asset': asset, 'change': data['change_24h']}})
        
        return alerts

    def _determine_route(self, macro_data):
        dxy = macro_data.get('dxy', 100)
        inflation = macro_data.get('inflation', 2.5)
        
        if inflation > 5.0 or dxy < 97:
            return "GOLD_RESERVE (PAXG/BTC)"
        if dxy > 105:
            return "CASH_REFUGE (USD)"
        return "STABLE_HYBRID (PAXG/USD)"

    def _get_action_description(self, level, route):
        if level == 1: return "Liquidation of asset to BTC + 48h Cooling-off"
        if level == 2: return f"Protocol PARACHUTE: Exit to {route} + BTC Hedge"
        if level == 3: return "TOTAL EXIT: Emergency Swap to PAXG/CHF"
        return "Normal Monitoring"

    def _execute_technical_orders(self, level, alert, route, active_positions):
        """Заглушки для виклику Kraken CLI"""
        if level == 1:
            asset = alert['data']['asset']
            self.lock_until[asset] = datetime.now() + timedelta(hours=48)
            # os.system(f"kraken trade sell {asset} --target XBT")
        
        if level >= 2:
            self.emergency_mode = True
            # os.system("kraken trade sell --all --target SAFE_ASSET")

    def _log_emergency(self, level, alert, action, route):
        """Запис у загальну історію для AI Guardian"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "ANTI_CRASH",
            "level": level,
            "action": action,
            "haven": route,
            "risk_score": self.risk_level,
            "reasoning": f"Triggered by level {level} alert. Data: {alert.get('data')}"
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")