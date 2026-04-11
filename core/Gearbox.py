import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Gearbox:
    def __init__(self, total_balance=10000):
        self.total_balance = total_balance
        
        # 1. СТРАТЕГІЧНІ НАЛАШТУВАННЯ
        self.config = {
            "RESERVE_PERCENT": 0.20,      # 20% завжди в кеші (страховка)
            "MAX_LOT_PER_PAIR": 1000.0,   # Не більше $1000 на одну монету
            "MIN_LOT_PER_ENGINE": 100.0,  # Мінімальний вхід $100
            "CRASH_THRESHOLD": 10.0       # Поріг активації Анти-краш
        }

        # 2. КОЕФІЦІЄНТИ ПРИБУТКОВОСТІ (Priority Multipliers)
        # Чим вище коефіцієнт, тим більше ваги отримує стратегія при рівних умовах
        self.efficiency = {
            "BULL_ENGINE": 1.5,      # Найприбутковіший (Пріоритет №1)
            "HOLD_ENGINE": 1.2,      # Фундамент (Пріоритет №2)
            "SIDEWAYS_ENGINE": 1.0,  # Грід-боти (Пріоритет №3)
            "SWING_ENGINE": 0.8,     # Свінг-трейдинг
            "BEAR_ENGINE": 0.5,      # Ведмежі стратегії (важче заробити)
            "ANTI_CRASH_ENGINE": 0.1 # Вмикається тільки примусово
        }

    def allocate_capital(self, market_segmentation):
        """
        Розрахунок капіталу з урахуванням ваги ринку, ККД стратегій та резерву.
        """
        # А) Вираховуємо робоче депо (мінус резерв)
        active_capital = self.total_balance * (1 - self.config["RESERVE_PERCENT"])
        allocation = {}

        # Б) Екстрений випадок (Анти-краш ігнорує коефіцієнти ККД)
        crash_weight = market_segmentation.get("6. CRASH", {}).get("weight", 0)
        if crash_weight >= self.config["CRASH_THRESHOLD"]:
            return self._emergency_distribution(active_capital)

        # В) Розрахунок "Рейтингу Попиту" (Weight * Efficiency)
        scores = {}
        total_score = 0
        
        mapping = {
            "2. BULLISH": "BULL_ENGINE",
            "5. HOLD": "HOLD_ENGINE",
            "1. SIDEWAYS": "SIDEWAYS_ENGINE",
            "4. PIG": "SWING_ENGINE",
            "3. BEARISH": "BEAR_ENGINE"
        }

        for reg_name, engine_key in mapping.items():
            weight = market_segmentation.get(reg_name, {}).get("weight", 0)
            if weight > 1.0: # Ігноруємо шум
                # Головна формула: Вага ринку * Коефіцієнт прибутковості
                score = weight * self.efficiency[engine_key]
                scores[engine_key] = score
                total_score += score

        # Г) Розподіл активного капіталу згідно з рейтингом
        if total_score > 0:
            for engine_key, score in scores.items():
                amount = active_capital * (score / total_score)
                
                # Д) Обмеження за кількістю пар (Диверсифікація)
                # Отримуємо кількість пар для цього режиму з сегментації
                reg_name = [k for k, v in mapping.items() if v == engine_key][0]
                pairs_count = len(market_segmentation.get(reg_name, {}).get("pairs", []))
                
                if pairs_count > 0:
                    # Максимально можлива сума для двигуна виходячи з ліміту лота
                    max_allowed = pairs_count * self.config["MAX_LOT_PER_PAIR"]
                    final_amount = min(amount, max_allowed)
                    
                    if final_amount >= self.config["MIN_LOT_PER_ENGINE"]:
                        allocation[engine_key] = round(final_amount, 2)

        return self._final_balancing(allocation)

    def _emergency_distribution(self, active_capital):
        """Протокол виживання"""
        return {
            "ANTI_CRASH_ENGINE": round(active_capital * 0.9, 2),
            "BEAR_ENGINE": round(active_capital * 0.1, 2)
        }

    def _final_balancing(self, allocation):
        """Повертає залишки в резерв, якщо ліміти не дозволили витратити все"""
        total_allocated = sum(allocation.values())
        # Все, що не влізло в ліміти $1000/пару, повертається в загальний кеш
        return allocation

if __name__ == "__main__":
    # ТЕСТ: Баланс $10,000. 20% резерв ($2000). Робочі - $8000.
    gb = Gearbox(10000)
    test_seg = {
        "2. BULLISH": {"weight": 50, "pairs": ["BTC", "ETH"]}, # Ліміт тут буде $2000
        "1. SIDEWAYS": {"weight": 50, "pairs": ["XRP", "ADA", "SOL", "DOT"]} # Тут ліміт $4000
    }
    # Оскільки BULLISH має вищий ККД (1.5), він отримає більше від своїх 50%, 
    # але буде обмежений лімітом пар ($2000).
    print(f"⚙️ Gearbox Smart Allocation: {gb.allocate_capital(test_seg)}")