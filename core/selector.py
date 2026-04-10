import subprocess
import json
import shutil
import time
import os

# Імпортуємо функцію та спільний список активів зі сканера (тепер з core)
try:
    from core.scanner import get_historical_stats, MARKET_ASSETS
except ImportError:
    from scanner import get_historical_stats, MARKET_ASSETS

# Глобальні змінні для кешування
_cached_segmentation = {}
_last_scan_time = 0

def select_best_pair(market_data):
    """
    Аналізує зібрані дані та повертає пару з найкращим сигналом.
    Якщо сигналів немає, повертає лідера за об'ємом.
    """
    if not market_data:
        return "XBTUSD"
    
    best_pair = "XBTUSD"
    max_score = -1.0
    
    for pair, stats in market_data.items():
        # Пріоритет парам з STRONG_BUY
        score = 1.0 if stats.get('ai_signal') == "STRONG_BUY" else 0.0
        # Додаємо волатильність як бонусний бал (якщо не занадто висока)
        score += (stats.get('volatility', 0) / 10.0)
        
        if score > max_score:
            max_score = score
            best_pair = pair
            
    return best_pair

def get_market_segmentation(market_data):
    """
    Головна функція для main.py. 
    Приймає готові дані сканера і групує їх по 6-ти сегментах.
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
    
    # Групуємо пари за режимами, які визначив сканер
    for pair, stats in market_data.items():
        regime = stats.get('regime', "1. SIDEWAYS")
        
        # Вираховуємо приблизний об'єм (базуємось на ціні)
        # В реальності тут краще використовувати дані Ticker, але для сегментації 
        # достатньо розподілу активів за кількістю та волатильністю
        vol_score = stats.get('volatility', 1.0) * stats.get('price', 1.0)
        
        if regime in segmentation:
            segmentation[regime]["count"] += 1
            segmentation[regime]["pairs"].append(pair)
            segmentation[regime]["vol_usd"] += vol_score
            total_market_vol += vol_score

    # Розрахунок ваги (Weight) для кожного сегмента
    for reg in segmentation:
        if total_market_vol > 0:
            segmentation[reg]["weight"] = round((segmentation[reg]["vol_usd"] / total_market_vol) * 100, 2)
        else:
            segmentation[reg]["weight"] = 0
            
    return segmentation

def display_segmentation_table(segmentation):
    """Виводить красиву таблицю в консоль (як ти любиш)"""
    print("\n" + "="*70)
    print(f"📊 MARKET SEGMENTATION REPORT | {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"{'REGIME':<18} | {'COUNT':<6} | {'WEIGHT (%)':<12} | {'ASSETS'}")
    print("-" * 70)
    
    for reg in sorted(segmentation.keys()):
        data = segmentation[reg]
        pairs_str = ", ".join(data['pairs'][:3]) + ("..." if len(data['pairs']) > 3 else "")
        print(f"{reg:<18} | {data['count']:<6} | {data['weight']:>10.1f}% | {pairs_str}")
    
    print("="*70)

# Стара функція для сумісності (якщо потрібно)
def get_market_sentiment(force_scan=False):
    # Ця логіка тепер делегована в main.py через get_market_segmentation
    # Але залишаємо її як проксі
    print("📝 Sentiment scan requested via Selector proxy.")
    return "1. SIDEWAYS", 0.0

if __name__ == "__main__":
    # Тестовий запуск
    test_data = {
        "XBTUSD": {"regime": "2. BULLISH", "price": 65000, "volatility": 2.1},
        "ETHUSD": {"regime": "1. SIDEWAYS", "price": 3500, "volatility": 1.5},
        "SOLUSD": {"regime": "2. BULLISH", "price": 145, "volatility": 4.5}
    }
    seg = get_market_segmentation(test_data)
    display_segmentation_table(seg)