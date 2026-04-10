import pandas as pd
import pandas_ta as ta
import os
import json
import gc
from datetime import datetime

class BullCylinder:
    """Індивідуальний тренд-адаптер для роботи на бичачому ринку"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        self.entry_price = 0
        
        # Налаштування індикаторів (Unit 3)
        self.rsi_period = 14
        self.ema_period = 200
        self.stoch_k = 14
        self.stoch_d = 3

    def analyze(self, df):
        """Логіка V2 Trend Pullback: RSI + EMA200 + Stochastic"""
        if df is None or len(df) < self.ema_period:
            return "HOLD", 0

        # Рахуємо індикатори
        df['rsi'] = ta.rsi(df['c'], length=self.rsi_period)
        df['ema_200'] = ta.ema(df['c'], length=self.ema_period)
        stoch = ta.stoch(df['h'], df['l'], df['c'], k=self.stoch_k, d=self.stoch_d)
        
        if stoch is None or df['ema_200'] is None:
            return "HOLD", 0

        stoch_k_col = stoch.columns[0]
        curr_price = df['c'].iloc[-1]
        row = {
            'close': curr_price,
            'ema_200': df['ema_200'].iloc[-1],
            'stoch_k': stoch[stoch_k_col].iloc[-1],
            'rsi': df['rsi'].iloc[-1]
        }
        prev_stoch_k = stoch[stoch_k_col].iloc[-2]

        # 1. УМОВИ ВХОДУ (Pullback у висхідному тренді)
        trend_up = row['close'] > row['ema_200']
        stoch_oversold = prev_stoch_k < 20  # Були в зоні перепроданості
        stoch_hook = row['stoch_k'] > prev_stoch_k # Почали розворот вгору
        
        if trend_up and stoch_oversold and stoch_hook and row['rsi'] < 60:
            return "BUY", curr_price
        
        # 2. УМОВИ ВИХОДУ (Перекупленість або злам тренду)
        if self.in_position:
            overbought = row['stoch_k'] > 85
            trend_broken = row['close'] < row['ema_200']
            if overbought or trend_broken:
                return "SELL", curr_price

        return "HOLD", curr_price

class BullEngine:
    def __init__(self):
        self.cylinders = {}
        self.log_path = "/home/ubuntu/03.KRAKEN_PROD/MAITS/state/trades_history.lsonl"

    def run_cycle(self, selected_pairs_data, global_budget):
        """Вхідна точка з main.py"""
        if not selected_pairs_data:
            return

        print(f"🚀 [BULL ENGINE] Hunting for Pullbacks in {len(selected_pairs_data)} assets...")
        budget_per_cyl = global_budget / len(selected_pairs_data)

        for p_data in selected_pairs_data:
            name = p_data['name']
            df = p_data.get('df') 
            
            if name not in self.cylinders:
                self.cylinders[name] = BullCylinder(name, budget_per_cyl)

            if df is not None:
                signal, price = self.cylinders[name].analyze(df)
                self.execute_logic(self.cylinders[name], signal, price)
            
            gc.collect()

    def execute_logic(self, cylinder, signal, price):
        """Виконання торгових команд та логування Reasoning"""
        pair = cylinder.pair
        
        if signal == "BUY" and not cylinder.in_position:
            reason = "Bullish Pullback: Price above EMA-200 and Stochastic recovery from oversold zone."
            print(f"   📈 [BULL ACTION] {pair} | BUY at {price}")
            print(f"      ∟ Reason: {reason}")
            
            cylinder.in_position = True
            cylinder.entry_price = price
            self.log_to_historian(pair, "BUY", price, reason)

        elif signal == "SELL" and cylinder.in_position:
            profit = ((price - cylinder.entry_price) / cylinder.entry_price) * 100
            reason = f"Taking Profit/Exit: Stochastic overbought (>85) or Trend reversal. Profit: {profit:.2f}%"
            print(f"   💰 [BULL ACTION] {pair} | SELL at {price}")
            print(f"      ∟ Reason: {reason}")
            
            cylinder.in_position = False
            self.log_to_historian(pair, "SELL", price, reason, profit)

    def log_to_historian(self, pair, action, price, reason, profit=0):
        """Запис для AI Guardian"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "BULL",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0,
            "reasoning": reason
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")