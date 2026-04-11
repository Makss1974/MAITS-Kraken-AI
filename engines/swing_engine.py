import os
import json
import gc
import pandas as pd
import pandas_ta as ta
from datetime import datetime

class SwingCylinder:
    """Individual Trend Analyzer for a specific trading pair"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        self.entry_price = 0
        
        # --- TECHNICAL CONFIGURATION ---
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.ema_period = 100
        
        print(f"   💎 [CYLINDER] {pair}: Trend Analysis Core initialized (EMA {self.ema_period}).")

    def analyze(self, df):
        """Calculates trend signals using MACD Cross and EMA Filter"""
        if df is None or len(df) < self.ema_period:
            return "HOLD", 0

        # Calculate Indicators using pandas_ta
        # Note: We ensure the data is compatible with TA-Lib logic
        macd = df.ta.macd(close='c', fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
        ema = df.ta.ema(close='c', length=self.ema_period)

        if macd is None or ema is None:
            return "HOLD", 0

        # Extracting MACD Line and Signal Line
        # MACD Column names usually follow 'MACD_12_26_9' format
        m_col = macd.columns[0] # MACD Line
        s_col = macd.columns[2] # Signal Line
        
        curr_m, curr_s = macd[m_col].iloc[-1], macd[s_col].iloc[-1]
        prev_m, prev_s = macd[m_col].iloc[-2], macd[s_col].iloc[-2]
        
        curr_price = df['c'].iloc[-1]
        curr_ema = ema.iloc[-1]

        # LOGIC 1: Bullish MACD Cross + Price Above EMA (Safe Uptrend)
        if (curr_m > curr_s and prev_m <= prev_s) and (curr_price > curr_ema):
            return "BUY", curr_price
        
        # LOGIC 2: Bearish MACD Cross (Trend Weakness)
        if (curr_m < curr_s and prev_m >= prev_s):
            return "SELL", curr_price

        return "HOLD", curr_price

class SwingEngine:
    """Manages multi-pair swing trading strategies for volatile markets"""
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
            print(f"\n🦾 [SWING ENGINE]: High-volatility 'PIG' mode detected. "
                  f"Searching for Trend Reversals with budget: ${global_budget:.2f}...")
            self.first_run = False
        else:
            print(f"\n⚙️  [SWING ENGINE]: Monitoring {len(selected_pairs_data)} trend cylinders.")

        # Distribute budget evenly across detected pairs
        budget_per_cyl = global_budget / len(selected_pairs_data)
        
        for p_data in selected_pairs_data:
            name = p_data['name']
            df = p_data.get('df') # Historical OHLCV data
            
            if name not in self.cylinders:
                self.cylinders[name] = SwingCylinder(name, budget_per_cyl)
            else:
                self.cylinders[name].budget = budget_per_cyl

            if df is not None:
                signal, price = self.cylinders[name].analyze(df)
                self.execute_swing_logic(self.cylinders[name], signal, price)
            
            gc.collect()

    def execute_swing_logic(self, cylinder, signal, price):
        """Execution logic with detailed narrative for PuTTY console"""
        pair = cylinder.pair
        
        reasoning = ""
        action_triggered = False

        if signal == "BUY" and not cylinder.in_position:
            reasoning = f"Bullish MACD crossover detected while price ({price:.2f}) stays above EMA {cylinder.ema_period}."
            print(f"   🚀 [TREND ACTION] {pair}: {reasoning} -> Entering LONG position.")
            
            cylinder.in_position = True
            cylinder.entry_price = price
            action_triggered = True
            self.log_to_historian(pair, "BUY", price, reasoning)

        elif signal == "SELL" and cylinder.in_position:
            profit = ((price - cylinder.entry_price) / cylinder.entry_price) * 100
            reasoning = f"Bearish MACD crossover detected. Protecting capital. Closing trend position."
            print(f"   🔻 [TREND ACTION] {pair}: {reasoning} -> Result: {profit:+.2f}% profit.")
            
            cylinder.in_position = False
            action_triggered = True
            self.log_to_historian(pair, "SELL", price, reasoning, profit)

        elif not action_triggered:
            # Periodic status for logs (Optional, to keep console clean we don't print HOLD every time)
            pass

    def log_to_historian(self, pair, action, price, reason, profit=0):
        """Standard LSONL logging for AI Guardian & Historian"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "SWING",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0, # Handled by AI Guardian
            "reasoning": reason
        }
        
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")