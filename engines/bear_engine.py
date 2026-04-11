import os
import json
import gc
import pandas as pd
import pandas_ta as ta
from datetime import datetime

class BearCylinder:
    """Individual defensive module for Bear Market operations"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.ema_period = 200
        print(f"   💎 [CYLINDER] {pair}: Defensive protocols loaded. Monitoring EMA-{self.ema_period} resistance.")

    def select_strategy(self, df, macro_risk):
        """Determines the bear market tactic based on technicals and macro risk levels"""
        if df is None or len(df) < self.ema_period:
            return "STABLE_SHIELD", 0, "Insufficient data for analysis. Priority: Capital Preservation."

        curr_price = df['c'].iloc[-1]
        rsi = ta.rsi(df['c'], length=14).iloc[-1]
        ema_200 = ta.ema(df['c'], length=self.ema_period).iloc[-1]
        
        # 1. VULTURE STRATEGY - Bottom fishing during extreme panic
        if rsi < 25 and macro_risk > 60:
            target_price = curr_price * (1 - 0.15) # Bid 15% lower than current
            return "VULTURE", target_price, f"Extreme oversold RSI ({rsi:.1f}) detected. Macro Panic Index high ({macro_risk})."

        # 2. SHORT STRATEGY - Active betting against the trend (Major assets only)
        is_major = any(m in self.pair for m in ["XBT", "BTC", "ETH"])
        if is_major and curr_price < ema_200:
            return "SHORT", curr_price, "Confirmed downtrend below long-term EMA-200. Major asset detected."

        # 3. SHIELD STRATEGY - Total safety mode
        return "STABLE_SHIELD", 0, "Market weakness detected. Maintaining capital in stable base currency."

class BearEngine:
    """Manages defensive maneuvers and short-selling during Bearish regimes"""
    def __init__(self):
        self.cylinders = {}
        self.base_dir = "/home/ubuntu/03.KRAKEN_PROD/MAITS"
        self.log_path = os.path.join(self.base_dir, "state/trades_history.lsonl")
        self.first_run = True

    def run_cycle(self, selected_pairs_data, global_budget):
        if not selected_pairs_data:
            return

        # --- XAI NARRATIVE: Engine Initialization ---
        if self.first_run:
            print(f"\n🐻 [BEAR ENGINE]: Bearish regime confirmed. "
                  f"Activating Risk Mitigation protocols with budget: ${global_budget:.2f}...")
            self.first_run = False
        else:
            print(f"\n⚙️  [BEAR ENGINE]: Evaluating {len(selected_pairs_data)} defensive cylinders.")

        budget_per_cyl = global_budget / len(selected_pairs_data)
        # Macro risk factor (e.g., from Fear & Greed index or market sentiment)
        macro_risk = 65 

        for p_data in selected_pairs_data:
            name = p_data['name']
            df = p_data.get('df')

            if name not in self.cylinders:
                self.cylinders[name] = BearCylinder(name, budget_per_cyl)

            cylinder = self.cylinders[name]
            cylinder.budget = budget_per_cyl
            strategy, target_p, reason = cylinder.select_strategy(df, macro_risk)
            
            self.execute_bear_logic(cylinder, strategy, target_p, reason)
            gc.collect()

    def execute_bear_logic(self, cylinder, strategy, target_price, reason):
        """Execution of defensive orders with technical justification"""
        pair = cylinder.pair
        
        if strategy == "STABLE_SHIELD":
            print(f"   🛡️ [SHIELD] {pair}: {reason} -> Holding stable balance.")
            self.log_to_historian(pair, "STABLE_EXIT", 0, reason)

        elif strategy == "VULTURE":
            print(f"   🦅 [VULTURE] {pair}: {reason} -> Placing deep limit BUY at {target_price:.2f}.")
            self.log_to_historian(pair, "LIMIT_BUY_VULTURE", target_price, reason)

        elif strategy == "SHORT":
            print(f"   📉 [SHORT] {pair}: {reason} -> Opening active SHORT position at {target_price:.2f}.")
            self.log_to_historian(pair, "OPEN_SHORT", target_price, reason)

    def log_to_historian(self, pair, action, price, reason):
        """Standard LSONL logging for AI Guardian and Audit compliance"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "BEAR",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": 0.0,
            "mdd": 0.0, # Handled by AI Guardian
            "reasoning": reason
        }
        
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")