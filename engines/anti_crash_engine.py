import os
import json
import gc
from datetime import datetime, timedelta

class MessageConstructor:
    """Generates high-fidelity reports for Console UX and AI Guardian Audit"""
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
            1: f"Asset {trigger_data.get('asset')} dropped {trigger_data.get('change')}% while BTC remains stable.",
            2: f"Systemic Panic: BTC dropped {trigger_data.get('btc_change')}%. Market Risk Index: {risk_score}/100.",
            3: f"Critical USDT De-peg ({trigger_data.get('usdt_price')}) or DXY Collapse. Global Liquidity Threat."
        }

        report = (
            f"\n{header}\n"
            f"⏰ Time: {timestamp} | Risk Score: {risk_score}/100\n"
            f"🧐 Analysis: {logic_map.get(level)}\n"
            f"⚡ Action: {action_taken}\n"
            f"⚓ Refuge: {target_haven}\n"
            f"__________________________________\n"
            f"🤖 MAITS Anti-Crash Unit v3.0"
        )
        return report

class AntiCrashEngine:
    """Main Defense Hub: Detects anomalies and executes emergency capital migration"""
    def __init__(self):
        self.emergency_mode = False
        self.lock_until = {} 
        self.risk_level = 0
        self.base_dir = "/home/ubuntu/03.KRAKEN_PROD/MAITS"
        self.log_path = os.path.join(self.base_dir, "state/trades_history.lsonl")
        
        # Defensive Assets Configuration
        self.safe_havens = {
            "HARD": ["PAXG", "XAUT"],        # Gold-backed tokens
            "ANTI_DXY": ["CHF", "JPY"],      # Safe-haven Fiats
            "FIAT": ["USD", "EUR"],          # Cash
            "RESERVE": ["BTC"]               # Digital Reserve
        }

    def run_cycle(self, market_data, macro_data=None, news_feed=None):
        """Primary Entry Point called by MaitsController during high-risk regimes"""
        self.risk_level = 0
        # Default empty values if not provided
        macro_data = macro_data or {}
        news_feed = news_feed or []
        
        alerts = self._scan_threats(market_data, macro_data, news_feed)
        
        if not alerts:
            return None

        # Process the most critical threat (highest level)
        alert = sorted(alerts, key=lambda x: x['level'], reverse=True)[0]
        level = alert['level']
        
        # Determine the best refuge based on Macro environment
        route = self._determine_route(macro_data)
        action_desc = self._get_action_description(level, route)
        
        # Generate Narrative for PuTTY Console
        report = MessageConstructor.create_report(
            level=level,
            trigger_data=alert.get('data', {}),
            action_taken=action_desc,
            target_haven=route,
            risk_score=self.risk_level
        )
        
        # Technical Execution (Audit Logging)
        self._log_emergency(level, alert, action_desc, route)
        self._execute_technical_orders(level, alert, route)
        
        print(report)
        return report

    def _scan_threats(self, market_data, macro_data, news_feed):
        """Scans for multi-level financial threats"""
        alerts = []
        
        # Check BTC/XBT stability (Market Anchor)
        btc_data = market_data.get('XBTUSD') or market_data.get('BTCUSD') or {}
        btc_change = btc_data.get('change_24h', 0)
        
        # LEVEL 3: Global De-peg or DXY Crash
        usdt_price = market_data.get('USDT', {}).get('price', 1.0)
        if usdt_price < 0.96 or macro_data.get('dxy_crash', False):
            self.risk_level = 100
            alerts.append({'level': 3, 'data': {'usdt_price': usdt_price}})
            return alerts # Immediate escalation

        # LEVEL 2: Systemic Market Panic
        panic_keywords = ["hack", "sec", "ban", "depeg", "liquidation", "insolvent"]
        panic_news = any(word in n.lower() for n in news_feed for word in panic_keywords)
        
        if btc_change <= -10.0 or panic_news:
            self.risk_level = 75
            alerts.append({'level': 2, 'data': {'btc_change': btc_change}})

        # LEVEL 1: Localized Asset Crash (Pump & Dump protection)
        for asset, data in market_data.items():
            if "XBT" not in asset and data.get('change_24h', 0) <= -12.0 and btc_change > -4.0:
                if asset not in self.lock_until or datetime.now() > self.lock_until[asset]:
                    alerts.append({'level': 1, 'data': {'asset': asset, 'change': data['change_24h']}})
        
        return alerts

    def _determine_route(self, macro_data):
        """Intelligently selects the refuge asset based on DXY and Inflation"""
        dxy = macro_data.get('dxy', 100)
        inflation = macro_data.get('inflation', 2.5)
        
        if inflation > 5.0 or dxy < 97:
            return "GOLD_RESERVE (PAXG)"
        if dxy > 105:
            return "CASH_REFUGE (USD)"
        return "STABLE_HYBRID (PAXG/USD)"

    def _get_action_description(self, level, route):
        if level == 1: return "Liquidation of high-risk asset to BTC + 48h Cooling-off"
        if level == 2: return f"Protocol PARACHUTE: Market-wide exit to {route} + BTC Hedge"
        if level == 3: return "TOTAL EXIT: Emergency Swap to PAXG (Hard Assets)"
        return "Normal Monitoring"

    def _execute_technical_orders(self, level, alert, route):
        """Kraken CLI Command Simulation (PAPER Trading)"""
        if level == 1:
            asset = alert['data']['asset']
            self.lock_until[asset] = datetime.now() + timedelta(hours=48)
            # Simulated Command: kraken trade sell {asset} --target XBT
        
        if level >= 2:
            self.emergency_mode = True
            # Simulated Command: kraken trade sell --all --target {route}

    def _log_emergency(self, level, alert, action, route):
        """LSONL Logging for AI Guardian and performance tracking"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "ANTI_CRASH",
            "level": level,
            "action": action,
            "haven": route,
            "risk_score": self.risk_level,
            "reasoning": f"Emergency triggered at level {level}. Trigger Data: {alert.get('data')}"
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")