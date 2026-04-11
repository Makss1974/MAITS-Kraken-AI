import os
import json
import gc
import pandas as pd
import pandas_ta as ta
from datetime import datetime

class HoldCylinder:
    """Individual HODL container with autonomous trailing stop logic"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        
        # Position tracking
        self.buy_price = 0
        self.highest_price = 0
        
        # Strategy Configuration
        self.ema_period = 200
        self.entry_threshold = -0.12     # Buy if price is 12% below EMA-200
        self.trailing_activation = 0.10  # Activate trailing after +10% gain
        self.trailing_dist = 0.05       # Trail distance (5%)
        
        print(f"   💎 [CYLINDER] {pair}: HODL Strategy initialized. "
              f"Entry Target: <{self.entry_threshold*100}% from EMA-{self.ema_period}")

    def update_peak(self, current_price):
        """Updates the highest price reached since entry for trailing stop calculation"""
        if self.in_position and current_price > self.highest_price:
            self.highest_price = current_price

class HoldEngine:
    """Manages strategic long-term accumulation and trailing exits"""
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
            print(f"\n🧘 [HOLD ENGINE]: Zen Mode active. "
                  f"Searching for extreme market discounts with budget: ${global_budget:.2f}...")
            self.first_run = False
        else:
            print(f"\n⚙️  [HOLD ENGINE]: Managing {len(selected_pairs_data)} long-term accumulation cylinders.")

        budget_per_cyl = global_budget / len(selected_pairs_data)

        for p_data in selected_pairs_data:
            name = p_data['name']
            price = p_data.get('price', 0)
            df = p_data.get('df')

            if name not in self.cylinders:
                self.cylinders[name] = HoldCylinder(name, budget_per_cyl)

            cylinder = self.cylinders[name]
            cylinder.budget = budget_per_cyl
            cylinder.update_peak(price)

            # Execution Logic
            if cylinder.in_position:
                self.execute_exit_logic(cylinder, price)
            elif df is not None:
                self.execute_entry_logic(cylinder, df)

            gc.collect()

    def execute_entry_logic(self, cylinder, df):
        """Detects extreme price deviations from the long-term mean (EMA-200)"""
        if len(df) < cylinder.ema_period:
            return

        # Calculate EMA-200
        ema = df.ta.ema(close='c', length=cylinder.ema_period).iloc[-1]
        curr_price = df['c'].iloc[-1]
        deviation = (curr_price - ema) / ema

        # Decision: If price is significantly below EMA, it's a value buy
        if deviation <= cylinder.entry_threshold:
            reasoning = (f"Extreme market dip detected. Asset is trading at {deviation:.2%} "
                         f"below EMA-{cylinder.ema_period}. Executing accumulation buy.")
            
            print(f"   🎯 [STRATEGIC BUY] {cylinder.pair}: {reasoning}")
            
            cylinder.in_position = True
            cylinder.buy_price = curr_price
            cylinder.highest_price = curr_price
            
            self.log_to_historian(cylinder.pair, "BUY", curr_price, reasoning)

    def execute_exit_logic(self, cylinder, current_price):
        """Dynamic Trailing Stop to protect significant gains"""
        peak_profit = (cylinder.highest_price - cylinder.buy_price) / cylinder.buy_price
        
        # Trailing logic activates only after target profit is reached
        if peak_profit >= cylinder.trailing_activation:
            exit_trigger_price = cylinder.highest_price * (1 - cylinder.trailing_dist)
            
            if current_price <= exit_trigger_price:
                final_profit = (current_price - cylinder.buy_price) / cylinder.buy_price * 100
                reasoning = (f"Trailing Stop triggered. Highest profit reached: {peak_profit:.2%}. "
                             f"Closing position to secure {final_profit:.2f}% gain.")
                
                print(f"   💰 [STRATEGIC SELL] {cylinder.pair}: {reasoning}")
                
                cylinder.in_position = False
                self.log_to_historian(cylinder.pair, "SELL", current_price, reasoning, final_profit)

    def log_to_historian(self, pair, action, price, reason, profit=0):
        """Standardized LSONL logging for AI Guardian and performance tracking"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "HOLD",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0, # Managed by AI Guardian Auditor
            "reasoning": reason
        }
        
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")