import pandas as pd
import pandas_ta as ta
import os
import json
import gc
from datetime import datetime

class BearCylinder:
    """Індивідуальний захисний модуль для ведмежого ринку"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.strategy_mode = "WAITING"
        self.ema_period = 200

    def select_strategy(self, df, macro_risk):
        """Вирішує, яку ведмежу тактику застосувати на основі ризиків та RSI"""
        if df is None or len(df) < self.ema_period:
            return "STABLE_SHIELD", 0, "Insufficient data, protecting capital"

        curr_price = df['c'].iloc[-1]
        rsi = ta.rsi(df['c'], length=14).iloc[-1]
        ema_200 = ta.ema(df['c'], length=self.ema_period).iloc[-1]
        
        # 1. ЛОГІКА СТЕРВ'ЯТНИКА (VULTURE) - Глибокий підбір при паніці
        if rsi < 25 and macro_risk > 60:
            target_price = curr_price * (1 - 0.15)
            return "VULTURE", target_price, f"Extreme oversold RSI ({rsi:.1f}) + Panic High"

        # 2. ЛОГІКА ШОРТУ (SHORT) - Тільки для BTC/ETH (Major assets)
        is_major = any(m in self.pair for m in ["XBT", "BTC", "ETH"])
        if is_major and curr_price < ema_200:
            return "SHORT", curr_price, "Major asset in confirmed downtrend (Below EMA-200)"

        # 3. ЛОГІКА ЩИТА (STABLE_SHIELD) - Безпека понад усе
        return "STABLE_SHIELD", 0, "Preserving capital during market weakness"

class BearEngine:
    def __init__(self):
        self.cylinders = {}
        self.log_path = "/home/ubuntu/03.KRAKEN_PROD/MAITS/state/trades_history.lsonl"

    def run_cycle(self, selected_pairs_data, global_budget):
        """Точка входу з main.py"""
        if not selected_pairs_data:
            return

        print(f"🐻 [BEAR ENGINE] Defensive Mode Active. Processing {len(selected_pairs_data)} pairs...")
        budget_per_cyl = global_budget / len(selected_pairs_data)

        # Макро-ризик (можна отримувати з Gearbox, тут ставимо 65 для прикладу паніки)
        macro_risk = 65 

        for p_data in selected_pairs_data:
            name = p_data['name']
            df = p_data.get('df')

            if name not in self.cylinders:
                self.cylinders[name] = BearCylinder(name, budget_per_cyl)

            cylinder = self.cylinders[name]
            strategy, target_p, reason = cylinder.select_strategy(df, macro_risk)
            
            self.execute_bear_logic(cylinder, strategy, target_p, reason)
            gc.collect()

    def execute_bear_logic(self, cylinder, strategy, target_price, reason):
        """Виконання захисних або шорт-команд"""
        pair = cylinder.pair
        
        if strategy == "STABLE_SHIELD":
            print(f"   🛡️ [SHIELD] {pair}: Exiting to USDT. Reason: {reason}")
            # self.kraken_sell_all(pair)
            self.log_to_historian(pair, "EXIT_SHIELD", 0, reason)

        elif strategy == "VULTURE":
            print(f"   🦅 [VULTURE] {pair}: Setting deep limit BUY at {target_price:.2f}")
            print(f"      ∟ Reason: {reason}")
            # self.place_limit_order(pair, target_price, cylinder.budget)
            self.log_to_historian(pair, "LIMIT_BUY_VULTURE", target_price, reason)

        elif strategy == "SHORT":
            print(f"   📉 [SHORT] {pair}: Opening 2x Short at {target_price:.2f}")
            print(f"      ∟ Reason: {reason}")
            # self.open_short(pair, target_price, cylinder.budget)
            self.log_to_historian(pair, "OPEN_SHORT", target_price, reason)

    def log_to_historian(self, pair, action, price, reason):
        """Фіксація дій для AI Guardian"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "BEAR",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": 0.0, # Зазвичай фіксується при закритті
            "mdd": 0.0,
            "reasoning": reason
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")