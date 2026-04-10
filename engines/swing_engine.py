import pandas as pd
import pandas_ta as ta
import os
import json
import gc
from datetime import datetime

class SwingCylinder:
    """Індивідуальний трендовий аналізатор для конкретної пари"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        self.entry_price = 0
        
        # Налаштування індикаторів (можна адаптувати під волатильність)
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.ema_period = 100

    def analyze(self, df):
        """Розрахунок сигналів на реальних даних (OHLCV)"""
        if df is None or len(df) < self.ema_period:
            return "HOLD", 0

        # Рахуємо технічні індикатори
        macd = df.ta.macd(close='c', fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
        ema = df.ta.ema(close='c', length=self.ema_period)

        if macd is None or ema is None:
            return "HOLD", 0

        # Поточні та попередні значення для визначення перетину
        m_col, s_col = macd.columns[0], macd.columns[2]
        curr_m, curr_s = macd[m_col].iloc[-1], macd[s_col].iloc[-1]
        prev_m, prev_s = macd[m_col].iloc[-2], macd[s_col].iloc[-2]
        
        curr_price = df['c'].iloc[-1]
        curr_ema = ema.iloc[-1]

        # ЛОГІКА: Перетин MACD знизу вгору + ціна вище EMA 100
        if (curr_m > curr_s and prev_m <= prev_s) and (curr_price > curr_ema):
            return "BUY", curr_price
        
        # ЛОГІКА ВИХОДУ: Перетин MACD зверху вниз
        if (curr_m < curr_s and prev_m >= prev_s):
            return "SELL", curr_price

        return "HOLD", curr_price

class SwingEngine:
    def __init__(self):
        self.cylinders = {}
        self.log_path = "/home/ubuntu/03.KRAKEN_PROD/MAITS/state/trades_history.lsonl"

    def run_cycle(self, selected_pairs_data, global_budget):
        """Вхідна точка з main.py"""
        if not selected_pairs_data:
            return

        print(f"📊 [SWING ENGINE] Scanning {len(selected_pairs_data)} pairs for Trend Signals...")
        
        # Виділяємо ліміт на кількість одночасних позицій (наприклад, 3 слоти)
        budget_per_slot = global_budget / 3 

        for p_data in selected_pairs_data:
            name = p_data['name']
            
            # Ініціалізація циліндра, якщо новий
            if name not in self.cylinders:
                self.cylinders[name] = SwingCylinder(name, budget_per_slot)

            # 1. Отримання даних (df має передаватися з Scanner або завантажуватися тут)
            # Припустимо, Scanner вже підготував df у p_data['df']
            df = p_data.get('df') 
            
            if df is not None:
                signal, price = self.cylinders[name].analyze(df)
                self.execute_swing_logic(self.cylinders[name], signal, price)
            
            gc.collect()

    def execute_swing_logic(self, cylinder, signal, price):
        """Виконання реальних дій на основі сигналів"""
        pair = cylinder.pair
        
        if signal == "BUY" and not cylinder.in_position:
            reason = f"Bullish Cross-Over detected. Price {price} is above EMA {cylinder.ema_period}."
            print(f"   🚀 [SWING ACTION] {pair} | BUY at {price}")
            print(f"      ∟ Reason: {reason}")
            
            cylinder.in_position = True
            cylinder.entry_price = price
            self.log_to_historian(pair, "BUY", price, reason)

        elif signal == "SELL" and cylinder.in_position:
            profit = ((price - cylinder.entry_price) / cylinder.entry_price) * 100
            reason = f"Bearish MACD Cross. Closing trend position with {profit:.2f}% profit."
            print(f"   🔻 [SWING ACTION] {pair} | SELL at {price}")
            print(f"      ∟ Reason: {reason}")
            
            cylinder.in_position = False
            self.log_to_historian(pair, "SELL", price, reason, profit)

    def log_to_historian(self, pair, action, price, reason, profit=0):
        """Запис для AI Guardian"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "SWING",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0, # MDD розраховується в аналітиці
            "reasoning": reason
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")