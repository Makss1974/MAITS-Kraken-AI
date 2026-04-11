import time
import json
import os
import gc
import sys
from datetime import datetime

# BASE_DIR - Єдиний робочий каталог проекту
BASE_DIR = "/home/ubuntu/03.KRAKEN_PROD/MAITS"
sys.path.append(os.path.join(BASE_DIR, 'core'))

# Core Tool Imports
from core.Gearbox import Gearbox  # Переконайтеся, що файл називається Gearbox.py
from core.scanner import get_historical_stats, MARKET_ASSETS
from core.selector import get_market_segmentation, display_segmentation_table
from core.ai_guardian import perform_final_audit
from core.analyst import BotAnalyst

# Конфігурація шляхів та бюджету
LOG_FILE = os.path.join(BASE_DIR, "state/trades_history.lsonl")
TOTAL_BUDGET = 5000.0

# Ініціалізація аналітика та коробки передач
analyst = BotAnalyst(log_path=LOG_FILE, start_balance=TOTAL_BUDGET)
gearbox = Gearbox(total_balance=TOTAL_BUDGET)

# Імпорт двигунів
try:
    from engines.anti_crash_engine import AntiCrashEngine
    from engines.bear_engine import BearEngine
    from engines.bull_engine import BullEngine
    from engines.hold_engine import HoldEngine 
    from engines.sideways_engine import SidewaysEngine
    from engines.swing_engine import SwingEngine
    print("✅ All Engines loaded successfully.")
except ImportError as e:
    print(f"❌ Critical Engine Import Error: {e}")
    AntiCrashEngine = BearEngine = BullEngine = HoldEngine = SidewaysEngine = SwingEngine = None

class MaitsController:
    def __init__(self):
        os.makedirs(os.path.join(BASE_DIR, "state"), exist_ok=True)
        self.target_pairs = MARKET_ASSETS 
        
        self.engine_instances = {
            "SIDEWAYS_ENGINE": SidewaysEngine() if SidewaysEngine else None,
            "BULL_ENGINE": BullEngine() if BullEngine else None,
            "BEAR_ENGINE": BearEngine() if BearEngine else None,
            "SWING_ENGINE": SwingEngine() if SwingEngine else None,
            "HOLD_ENGINE": HoldEngine() if HoldEngine else None,
            "ANTI_CRASH_ENGINE": AntiCrashEngine() if AntiCrashEngine else None
        }
        self.last_regime = "N/A"
        self.last_engine = "N/A"

    def run_cycle(self):
        print(f"\n{'='*70}\n🚀 MAITS CYCLE | {datetime.now().strftime('%H:%M:%S')}")

        market_data = {}
        total_assets = len(self.target_pairs)
        print(f"🔍 Scanning {total_assets} assets via Kraken CLI...")
        
        for i, pair in enumerate(self.target_pairs):
            try:
                if (i + 1) % 10 == 0 or i + 1 == total_assets:
                    print(f"📊 Progress: {i+1}/{total_assets} assets scanned...")
                
                stats = get_historical_stats(pair)
                if stats:
                    market_data[pair] = stats
            except Exception as e:
                print(f"⚠️ Error scanning {pair}: {e}")

        if not market_data:
            print("❌ No market data collected. Skipping cycle.")
            return

        # 1. Аналіз ринку та сегментація
        segmentation = get_market_segmentation(market_data)
        display_segmentation_table(segmentation)

        # 2. Розподіл капіталу через Gearbox
        allocations = gearbox.allocate_capital(segmentation)
        
        # 3. ФАЗА ВИКОНАННЯ (Виправлений цикл запуску)
        for engine_key, budget in allocations.items():
            if budget <= 10: 
                continue
            
            # Визначаємо відповідний режим ринку для логів
            current_regime_name = "N/A"
            for reg_name in segmentation.keys():
                if engine_key.split('_')[0] in reg_name:
                    current_regime_name = reg_name
                    break

            self.last_engine = engine_key
            self.last_regime = current_regime_name

            # --- ФІКС: Фільтрація списку пар для двигуна ---
            pairs_list = segmentation.get(current_regime_name, {}).get('pairs', [])
            
            selected_pairs_data = []
            for p_name in pairs_list:
                if p_name in market_data:
                    p_info = market_data[p_name].copy()
                    p_info['name'] = p_name
                    selected_pairs_data.append(p_info)

            # Виклик двигуна
            engine = self.engine_instances.get(engine_key)
            if engine and selected_pairs_data:
                print(f"⚙️ Gearbox: Activating {engine_key} with ${budget:.2f}")
                try:
                    # Тепер передаємо СПИСОК словників, як того очікують двигуни
                    engine.run_cycle(selected_pairs_data, budget)
                except Exception as e:
                    print(f"⚠️ Engine {engine_key} failed: {e}")

        # 4. AI Guardian Audit
        print("\n🛡️ AI Guardian performing audit...")
        try:
            perform_final_audit(LOG_FILE)
        except Exception as e:
            print(f"⚠️ Audit failed: {e}")

        gc.collect()

if __name__ == "__main__":
    print(f"\n{'*' * 70}")
    print("🌟 HELLO, BOSS! I'm MAITS — your multi-gear trading system.")
    print(f"🤖 MAITS v2.4 ONLINE | Working Directory: {BASE_DIR}")
    print(f"{'*' * 70}\n")

    try:
        controller = MaitsController()
        while True:
            try:
                controller.run_cycle()
                
                # Оновлений моніторинг (Дашборд)
                analyst.display_dashboard(
                    active_engine_name=controller.last_engine, 
                    market_regime=controller.last_regime,
                    pairs_count=len(controller.target_pairs)
                )

            except Exception as cycle_error:
                print(f"⚠️ Emergency: Error during execution cycle: {cycle_error}")
            
            print(f"\n⏳ System in standby. Sleeping 5 minutes...")
            time.sleep(300)
    except KeyboardInterrupt:
        print("\n👋 System shutdown initiated by Boss. Goodbye!")
    except Exception as e:
        print(f"⚠️ Critical Runtime Error: {e}")