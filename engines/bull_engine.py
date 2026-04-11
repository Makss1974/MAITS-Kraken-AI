import os
import json
import gc
import pandas as pd
import pandas_ta as ta
from datetime import datetime

class BullCylinder:
    """Individual Trend Adapter for Bull Market operations"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        self.entry_price = 0
        
        # --- INDICATOR CONFIGURATION ---
        self.rsi_period = 14
        self.ema_period = 200
        self.stoch_k = 14
        self.stoch_d = 3
        
        print(f"   💎 [CYLINDER] {pair}: Bull-Trend logic active. Monitoring Pullbacks above EMA-{self.ema_period}.")

    def analyze(self, df):
        """V2 Trend Pullback Logic: RSI + EMA200 + Stochastic Optimizer"""
        if df is None or len(df) < self.ema_period:
            return "HOLD", 0

        # Technical Analysis
        df['rsi'] = ta.rsi(df['c'], length=self.rsi_period)
        df['ema_200'] = ta.ema(df['c'], length=self.ema_period)
        stoch = ta.stoch(df['h'], df['l'], df['c'], k=self.stoch_k, d=self.stoch_d)
        
        if stoch is None or df['ema_200'].isnull().all():
            return "HOLD", 0

        stoch_k_col = stoch.columns[0]
        curr_price = df['c'].iloc[-1]
        
        # Current and Previous states
        curr_ema = df['ema_200'].iloc[-1]
        curr_stoch_k = stoch[stoch_k_col].iloc[-1]
        prev_stoch_k = stoch[stoch_k_col].iloc[-2]
        curr_rsi = df['rsi'].iloc[-1]

        # 1. ENTRY CONDITIONS (Buying the Dip in an Uptrend)
        is_uptrend = curr_price > curr_ema
        is_stoch_reversing = prev_stoch_k < 20 and curr_stoch_k > prev_stoch_k
        is_not_overbought = curr_rsi < 60
        
        if not self.in_position:
            if is_uptrend and is_stoch_reversing and is_not_overbought:
                return "BUY", curr_price
        
        # 2. EXIT CONDITIONS (Overbought state or Trend Failure)
        if self.in_position:
            is_overbought = curr_stoch_k > 85
            is_trend_broken = curr_price < curr_ema
            if is_overbought or is_trend_broken:
                return "SELL", curr_price

        return "HOLD", curr_price

class BullEngine:
    """Manages aggressive trend-following strategies during Bullish regimes"""
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
            print(f"\n🚀 [BULL ENGINE]: Bullish regime confirmed. "
                  f"Initializing Pullback Hunter with budget: ${global_budget:.2f}...")
            self.first_run = False
        else:
            print(f"\n⚙️  [BULL ENGINE]: Scanning {len(selected_pairs_data)} assets for long entries.")

        budget_per_cyl = global_budget / len(selected_pairs_data)

        for p_data in selected_pairs_data:
            name = p_data['name']
            df = p_data.get('df') 
            
            if name not in self.cylinders:
                self.cylinders[name] = BullCylinder(name, budget_per_cyl)
            else:
                self.cylinders[name].budget = budget_per_cyl

            if df is not None:
                signal, price = self.cylinders[name].analyze(df)
                self.execute_logic(self.cylinders[name], signal, price)
            
            gc.collect()

    def execute_logic(self, cylinder, signal, price):
        """Action execution with institutional-grade reasoning for PuTTY logs"""
        pair = cylinder.pair
        
        if signal == "BUY" and not cylinder.in_position:
            reasoning = "Institutional Pullback detected: Price confirmed above EMA-200 with Stochastic momentum recovery."
            print(f"   📈 [BULL ACTION] {pair}: {reasoning} -> Executing LONG entry at {price:.2f}.")
            
            cylinder.in_position = True
            cylinder.entry_price = price
            self.log_to_historian(pair, "BUY", price, reasoning)

        elif signal == "SELL" and cylinder.in_position:
            profit = ((price - cylinder.entry_price) / cylinder.entry_price) * 100
            reasoning = f"Target reached: Stochastic overbought (>85) or trend exhaustion. Result: {profit:+.2f}%"
            print(f"   💰 [BULL ACTION] {pair}: {reasoning} -> Closing position at {price:.2f}.")
            
            cylinder.in_position = False
            self.log_to_historian(pair, "SELL", price, reasoning, profit)

    def log_to_historian(self, pair, action, price, reason, profit=0):
        """LSONL logging for AI Guardian audit and performance tracking"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "BULL",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0, # Calculated by AI Guardian
            "reasoning": reason
        }
        
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")