import time
import os
from prettytable import PrettyTable

# STEP 1: Імпорт єдиного списку активів та функцій зі сканера
# Використовуємо Rule 2025-12-29 щодо стабільності структури
try:
    from core.scanner import get_historical_stats, MARKET_ASSETS
except ImportError:
    # Для запусків напряму з папки core
    from scanner import get_historical_stats, MARKET_ASSETS

def select_best_pair(market_data):
    """
    Аналізує зібрані дані та повертає пару з найкращим сигналом.
    Використовує AI_SIGNAL та Volatility для скорингу.
    """
    if not market_data:
        return MARKET_ASSETS[0] if MARKET_ASSETS else "XBTUSD"
    
    best_pair = "XBTUSD"
    max_score = -1.0
    
    for pair, stats in market_data.items():
        # Скоринг: STRONG_BUY дає базовий бал
        score = 1.5 if stats.get('ai_signal') == "STRONG_BUY" else 0.0
        
        # Додаємо волатильність як фактор (чим вища в розумних межах, тим краще для ботів)
        vol = stats.get('volatility', 0)
        score += (vol / 10.0)
        
        if score > max_score:
            max_score = score
            best_pair = pair
            
    return best_pair

def get_market_segmentation(market_data):
    """
    Головна функція сегментації для main.py. 
    Групує всі 41 пару за 6-ма режимами GEARBOX.
    """
    segmentation = {
        "1. SIDEWAYS": {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0},
        "2. BULLISH":  {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0},
        "3. BEARISH":  {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0},
        "4. PIG":      {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0},
        "5. HOLD":     {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0},
        "6. CRASH":    {"count": 0, "vol_usd": 0, "pairs": [], "weight": 0}
    }
    
    total_market_vol = 0
    
    # Використовуємо дані, зібрані сканером по списку MARKET_ASSETS
    for pair, stats in market_data.items():
        regime = stats.get('regime', "1. SIDEWAYS")
        
        # Розрахунок "ваги" активу в поточному моменті
        vol_score = stats.get('volatility', 1.0) * stats.get('price', 1.0)
        
        if regime in segmentation:
            segmentation[regime]["count"] += 1
            segmentation[regime]["pairs"].append(pair)
            segmentation[regime]["vol_usd"] += vol_score
            total_market_vol += vol_score

    # Розрахунок Weight (%) для Gearbox
    for reg in segmentation:
        if total_market_vol > 0:
            segmentation[reg]["weight"] = round((segmentation[reg]["vol_usd"] / total_market_vol) * 100, 2)
        else:
            segmentation[reg]["weight"] = 0
            
    return segmentation

def display_segmentation_table(segmentation):
    """Візуалізація ринкових режимів у консоль PuTTY"""
    print("\n" + "="*70)
    print(f"📊 MARKET SEGMENTATION REPORT | {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    table = PrettyTable()
    table.field_names = ["REGIME", "COUNT", "WEIGHT (%)", "TOP ASSETS"]
    table.align["REGIME"] = "l"
    table.align["TOP ASSETS"] = "l"
    
    for reg in sorted(segmentation.keys()):
        data = segmentation[reg]
        # Показуємо перші 3 активи для компактності
        pairs_str = ", ".join(data['pairs'][:3]) + ("..." if len(data['pairs']) > 3 else "")
        table.add_row([
            reg, 
            data['count'], 
            f"{data['weight']}%", 
            pairs_str
        ])
    
    print(table)
    print("="*70)

if __name__ == "__main__":
    # Тестовий прогін з використанням списку зі сканера
    print(f"🔍 Testing Selector with global assets: {len(MARKET_ASSETS)} pairs found.")
    test_data = {
        MARKET_ASSETS[0]: {"regime": "2. BULLISH", "price": 65000, "volatility": 2.1},
        MARKET_ASSETS[1]: {"regime": "1. SIDEWAYS", "price": 3500, "volatility": 1.5}
    }
    seg = get_market_segmentation(test_data)
    display_segmentation_table(seg)
