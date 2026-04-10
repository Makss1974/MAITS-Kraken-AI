import os
import json
import logging
from datetime import datetime

# --- КОНФІГУРАЦІЯ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_BASE_DIR = os.path.join(BASE_DIR, "state/logs")

class Gearbox:
    def __init__(self, total_balance=5000):
        self.total_balance = total_balance
        os.makedirs(LOG_BASE_DIR, exist_ok=True)
        
        # Пріоритети прибутковості (Weights) згідно з твоєю логікою
        self.priorities = {
            "BULL": 0.40,    # 40% капіталу на ріст
            "HOLD": 0.25,    # 25% фундамент
            "PIG": 0.15,     # 15% Swing/Whipsaw
            "SIDEWAYS": 0.15, # 15% Боковик
            "BEAR": 0.05     # 5% Захист
        }

    def _setup_bot_log(self, bot_id):
        """Технічне логування згідно з Rule #2026-01-11"""
        # bot_id очікується як число або коротка назва (наприклад, 1, 2, 'bull')
        log_file = os.path.join(LOG_BASE_DIR, f"{bot_id}_bot.log")
        logger = logging.getLogger(f"Bot_{bot_id}")
        
        if not logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def allocate_capital(self, market_segmentation):
        """
        market_segmentation: dict від Selector.py 
        Приклад: {"2. BULLISH": {"weight": 60, ...}, "1. SIDEWAYS": {"weight": 30, ...}}
        """
        allocation = {}
        
        # 1. Екстрений захист: Якщо CRASH > 10% ваги ринку
        crash_data = market_segmentation.get("6. CRASH", {})
        if crash_data.get("weight", 0) > 10.0:
            print("🚨 GEARBOX: EMERGENCY PROTOCOL ACTIVATED (CRASH DETECTED)")
            return self._emergency_distribution()

        # 2. Динамічний розподіл за сегментами
        for regime, data in market_segmentation.items():
            weight_factor = data.get('weight', 0) / 100.0
            if weight_factor <= 0: continue

            if "BULLISH" in regime:
                allocation["BULL_ENGINE"] = self.total_balance * weight_factor * self.priorities["BULL"]
                allocation["HOLD_ENGINE"] = self.total_balance * weight_factor * self.priorities["HOLD"]
            
            elif "SIDEWAYS" in regime:
                allocation["SIDEWAYS_ENGINE"] = self.total_balance * weight_factor * self.priorities["SIDEWAYS"]

            elif "PIG" in regime:
                allocation["SWING_ENGINE"] = self.total_balance * weight_factor * self.priorities["PIG"]

            elif "BEARISH" in regime:
                allocation["BEAR_ENGINE"] = self.total_balance * weight_factor * self.priorities["BEAR"]

        return self._optimize_allocation(allocation)

    def _emergency_distribution(self):
        """Протокол виживання: 85% в Anti-Crash, 15% на короткі позиції"""
        return {
            "ANTI_CRASH_ENGINE": self.total_balance * 0.85,
            "BEAR_ENGINE": self.total_balance * 0.15
        }

    def _optimize_allocation(self, allocation):
        """Гарантуємо, що ми не витратимо більше, ніж маємо"""
        total_allocated = sum(allocation.values())
        if total_allocated > self.total_balance:
            factor = self.total_balance / total_allocated
            return {k: round(v * factor, 2) for k, v in allocation.items()}
        
        # Якщо залишилися вільні кошти (через низьку вагу сегментів), 
        # відправляємо їх у HOLD як резерв
        remaining = self.total_balance - total_allocated
        if remaining > 0:
            allocation["HOLD_ENGINE"] = allocation.get("HOLD_ENGINE", 0) + remaining
            
        return {k: round(v, 2) for k, v in allocation.items()}

if __name__ == "__main__":
    # Тест Gearbox
    gb = Gearbox(5000)
    sample_seg = {
        "2. BULLISH": {"weight": 70},
        "1. SIDEWAYS": {"weight": 20},
        "6. CRASH": {"weight": 5}
    }
    res = gb.allocate_capital(sample_seg)
    print(f"⚙️ Gearbox Allocation Test: {res}")