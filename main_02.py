import time
import json
import os
import gc
import sys
# STEP 1: Setting up paths for core modules (Rule 2025-12-29)
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Checking for pandas_ta before engine imports
try:
    import pandas_ta
except ImportError:
    print("⚠️ Warning: 'pandas_ta' not found. Please run: pip install pandas_ta")

# Core Tool Imports
from core.scanner import get_historical_stats
from core.selector import get_market_segmentation, display_segmentation_table
from core.historian import calculate_probabilities
from core.executor import execute_engine_command
from core.ai_guardian import perform_final_audit
from core.analyst import BotAnalyst
from datetime import datetime
from prettytable import PrettyTable

analyst = BotAnalyst(log_path="/home/ubuntu/01.KUCOIN_PROD/bots/bot_1/state/trades_history.lsonl")

# STEP 2: Engine Imports
try:
    from engines.anti_crash_engine import AntiCrashEngine as AntiKrashEngine
    from engines.bear_engine import BearEngine
    from engines.bull_engine import BullEngine
    from engines.hold_engine import HoldEngine 
    from engines.sideways_engine import SidewaysEngine
    from engines.swing_engine import SwingEngine
    print("✅ All Engines loaded successfully.")
except ImportError as e:
    print(f"❌ Critical Engine Import Error: {e}")
    AntiKrashEngine = BearEngine = BullEngine = HoldEngine = SidewaysEngine = SwingEngine = None

# --- CONFIGURATION ---
BASE_DIR = "/home/ubuntu/03.KRAKEN_PROD/MAITS"
STATE_DIR = os.path.join(BASE_DIR, "state")
LOG_FILE = os.path.join(STATE_DIR, "trades_history.lsonl")
TOTAL_BUDGET = 5000  

class MaitsController:
    def __init__(self):
        os.makedirs(STATE_DIR, exist_ok=True)
        
        # Extended Asset List (40+ pairs for full market analysis)
        self.target_pairs = [
            "XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "AVAXUSD",
            "LINKUSD", "LTCUSD", "BCHUSD", "SHIBUSD", "MATICUSD", "UNIUSD", "NEARUSD",
            "ICPUSD", "XLMUSD", "ETCUSD", "FILUSD", "XMRUSD", "ATOMUSD", "LDOUSD",
            "HBARUSD", "APTUSD", "ARBUSD", "VETUSD", "OPUSD", "GRTUSD", "RNDRUSD",
            "STXUSD", "MKRUSD", "INJUSD", "THETAUSD", "RUNEUSD", "TIAUSD", "AAVEUSD",
            "ALGOUSD", "EGLDUSD", "FLOWUSD", "KAVAUSD", "SANDUSD", "MANAUSD"
        ]
        
        self.engines = {
            "1. SIDEWAYS": SidewaysEngine() if SidewaysEngine else None,
            "2. BULLISH": BullEngine() if BullEngine else None,
            "3. BEARISH": BearEngine() if BearEngine else None,
            "4. PIG": SwingEngine() if SwingEngine else None,
            "5. HOLD": HoldEngine() if HoldEngine else None,
            "6. CRASH": AntiKrashEngine() if AntiKrashEngine else None
        }

    def allocate_resources(self, segmentation_report):
        allocations = {}
        print("\n💰 [GEARBOX] Resource Allocation:")
        
        for regime, data in segmentation_report.items():
            weight = data.get('weight', 0) / 100.0
            
            # Logic: Crash mode takes 80% if threat level is high
            if regime == "6. CRASH" and weight > 0.1:
                allocations[regime] = TOTAL_BUDGET * 0.8
            elif weight > 0.01:
                allocations[regime] = TOTAL_BUDGET * weight
            else:
                allocations[regime] = 0
            
            if allocations.get(regime, 0) > 0:
                print(f"   - {regime:<15}: ${allocations[regime]:>8.2f}")
        
        return allocations

    def run_cycle(self):
        print(f"\n{'='*70}\n🚀 MAITS CYCLE | {datetime.now().strftime('%H:%M:%S')}")

        market_data = {}
        total_assets = len(self.target_pairs)
        print(f"🔍 Scanning {total_assets} assets via Kraken CLI...")
        
        # Gathering all data before analysis
        for i, pair in enumerate(self.target_pairs):
            try:
                # Progress indicator for large scans
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

        # Market Analysis
        segmentation = get_market_segmentation(market_data)
        display_segmentation_table(segmentation)

        # Resource Allocation
        allocations = self.allocate_resources(segmentation)

        # Execution Phase
        for regime, budget in allocations.items():
            if budget <= 10: 
                continue
            
            pair_names = segmentation.get(regime, {}).get('pairs', [])
            pairs_with_stats = []
            
            for name in pair_names:
                if name in market_data:
                    data = market_data[name].copy()
                    data['name'] = name
                    pairs_with_stats.append(data)

            engine = self.engines.get(regime)
            
            if engine and pairs_with_stats:
                print(f"⚙️  Activating {regime} Engine...")
                try:
                    if hasattr(engine, 'run_cycle'):
                        engine.run_cycle(pairs_with_stats, budget)
                    else:
                        print(f"⚠️  Engine {regime} is missing 'run_cycle' method.")
                except Exception as e:
                    print(f"⚠️  Engine {regime} execution failed: {e}")

        # AI Guardian Audit
        print("\n🛡️  AI Guardian performing audit...")
        try:
            perform_final_audit(LOG_FILE)
        except Exception as e:
            print(f"⚠️  Audit failed: {e}")

        gc.collect()
        print(f"\n✅ Cycle finished successfully.")

def print_dashboard(analyst, active_engine, current_market):
    # Очищаємо екран для ефекту "Real-time"
    os.system('clear') 
    
    print(f"=== MAITS LIVE MONITORING | {datetime.now().strftime('%H:%M:%S')} ===")
    
    # Таблиця 1: Фінансова аналітика
    summary = analyst.get_summary_table()
    fin_table = PrettyTable()
    fin_table.field_names = ["Metric", "Value"]
    for k, v in summary.items():
        fin_table.add_row([k, v])
    print(fin_table)

    # Таблиця 2: Поточний стан системи
    status_table = PrettyTable()
    status_table.field_names = ["Active Engine", "Market Regime", "Pairs Scanned"]
    status_table.add_row([active_engine, current_market, "41"])
    print(status_table)
    
    print("\n[LOG]: " + "Scanning market regimes and auditing trades...")

if __name__ == "__main__":
    print(f"\n{'*' * 70}")
    print("🌟 HELLO, BOSS! I'm MAITS — your multi-gear trading system.")
    print(f"🤖 MAITS v2.4 ONLINE | Location: {BASE_DIR}")
    print(f"{'*' * 70}\n")

    try:
        controller = MaitsController()
        while True:
            try:
                controller.run_cycle()
            except Exception as cycle_error:
                print(f"⚠️ Emergency: Error during execution cycle: {cycle_error}")
            
            print(f"\n⏳ System in standby. Sleeping 5 minutes...")
            time.sleep(300)
    except KeyboardInterrupt:
        print("\n👋 System shutdown initiated by Boss. Goodbye!")
    except Exception as e:
        print(f"⚠️ Critical Runtime Error: {e}")