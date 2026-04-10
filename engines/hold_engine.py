import pandas as pd
import pandas_ta as ta
import os
import json
import gc
from datetime import datetime

class HoldCylinder:
    """Індивідуальний HODL-контейнер для активу"""
    def __init__(self, pair, budget):
        self.pair = pair
        self.budget = budget
        self.in_position = False
        
        # Стан позиції
        self.buy_price = 0
        self.highest_price = 0
        
        # Конфігурація стратегії (Rule: Scalability)
        self.ema_period = 200
        self.entry_threshold = -0.12  # Купуємо, якщо ціна на 12% нижче EMA-200
        self.trailing_activation = 0.10  # Трейлінг активується після +10%
        self.trailing_dist = 0.05      # Відстань відступу (5%)

    def update_state(self, current_price):
        """Оновлення пікової ціни для трейлінгу"""
        if self.in_position and current_price > self.highest_price:
            self.highest_price = current_price

class HoldEngine:
    def __init__(self):
        self.cylinders = {}
        self.log_path = "/home/ubuntu/03.KRAKEN_PROD/MAITS/state/trades_history.lsonl"

    def run_cycle(self, selected_pairs_data, global_budget):
        """Точка входу для MAITS"""
        if not selected_pairs_data:
            return

        print(f"🧘 [HOLD ENGINE] Monitoring {len(selected_pairs_data)} assets for deep entry points...")
        budget_per_cyl = global_budget / len(selected_pairs_data)

        for p_data in selected_pairs_data:
            name = p_data['name']
            price = p_data.get('price', 0)
            df = p_data.get('df') # OHLCV дані для розрахунку EMA

            if name not in self.cylinders:
                self.cylinders[name] = HoldCylinder(name, budget_per_cyl)

            cylinder = self.cylinders[name]
            cylinder.update_state(price)

            # 1. Перевірка виходу (якщо вже в позиції)
            if cylinder.in_position:
                self.check_exit_logic(cylinder, price)
            
            # 2. Перевірка входу (якщо ще немає позиції)
            elif df is not None:
                self.check_entry_logic(cylinder, df)

            gc.collect()

    def check_entry_logic(self, cylinder, df):
        """Пошук екстремального відхилення від середньої"""
        if len(df) < cylinder.ema_period:
            return

        # Розрахунок EMA-200
        ema = df.ta.ema(close='c', length=cylinder.ema_period).iloc[-1]
        curr_price = df['c'].iloc[-1]
        deviation = (curr_price - ema) / ema

        if deviation <= cylinder.entry_threshold:
            reason = f"Extreme dip detected: {deviation:.2%} below EMA-{cylinder.ema_period}."
            print(f"   🎯 [HOLD BUY] {cylinder.pair} | Price: {curr_price:.2f}")
            print(f"      ∟ Reason: {reason}")
            
            cylinder.in_position = True
            cylinder.buy_price = curr_price
            cylinder.highest_price = curr_price
            
            self.log_action(cylinder.pair, "BUY", curr_price, reason)

    def check_exit_logic(self, cylinder, current_price):
        """Динамічний трейлінг-стоп"""
        peak_profit = (cylinder.highest_price - cylinder.buy_price) / cylinder.buy_price
        
        # Активуємо трейлінг тільки після досягнення мінімального профіту
        if peak_profit >= cylinder.trailing_activation:
            exit_price = cylinder.highest_price * (1 - cylinder.trailing_dist)
            
            if current_price <= exit_price:
                profit_final = (current_price - cylinder.buy_price) / cylinder.buy_price * 100
                reason = f"Trailing Stop triggered. Peak profit was {peak_profit:.2%}. Final: {profit_final:.2f}%"
                
                print(f"   💰 [HOLD SELL] {cylinder.pair} | Price: {current_price:.2f}")
                print(f"      ∟ Reason: {reason}")
                
                cylinder.in_position = False
                self.log_action(cylinder.pair, "SELL", current_price, reason, profit_final)

    def log_action(self, pair, action, price, reason, profit=0):
        """Фіксація для AI Guardian та хакатон-звіту"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "HOLD",
            "pair": pair,
            "action": action,
            "price": price,
            "profit_pct": round(profit, 3),
            "mdd": 0.0, # Розрахує аудитор
            "reasoning": reason
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")