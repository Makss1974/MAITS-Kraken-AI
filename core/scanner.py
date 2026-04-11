import subprocess
import json
import shutil
import os
import time

# --- КОНФІГУРАЦІЯ ШЛЯХІВ ---
# Отримуємо шлях до MAITS незалежно від того, звідки запущено скрипт
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR)

# --- ПОВНИЙ СПИСОК 40 АКТИВІВ ---
MARKET_ASSETS = [
    "XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "ADAUSD", 
    "DOTUSD", "LINKUSD", "LTCUSD", "AVAXUSD", "TRXUSD",
    "UNIUSD", "ATOMUSD", "ETCUSD", "XLMUSD", "NEARUSD",
    "AAVEUSD", "ALGOUSD", "STXUSD", "ICPUSD", "GRTUSD",
    "SHIBUSD", "DOGEUSD", "PEPEUSD", "RENDERUSD", "FETUSD",
    "APTUSD", "OPUSD", "ARBUSD", "TIAUSD", "SUIUSD",
    "IMXUSD", "HBARUSD", "INJUSD", "FILUSD", "MKRUSD",
    "RUNEUSD", "EGLDUSD", "THETAUSD", "LDOUSD", "SEIUSD"
]

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gain = [d if d > 0 else 0 for d in deltas]
    loss = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gain[-period:]) / period
    avg_loss = sum(loss[-period:]) / period
    
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def get_composite_signal(prices, rsi):
    """AI Correlation Brain — обчислює ймовірність руху"""
    avg_price = sum(prices[-20:]) / 20
    current_price = prices[-1]
    dev = (current_price - avg_price) / avg_price * 100
    
    mean_score = -0.5 if dev > 2.0 else (0.4 if dev < -2.0 else 0)
    rsi_score = -0.5 if rsi > 70 else (0.4 if rsi < 30 else 0)
    total_score = mean_score + rsi_score
    
    if total_score >= 0.4: return "STRONG_BUY", total_score, dev
    if total_score <= -0.4: return "STRONG_SELL", total_score, dev
    return "NEUTRAL", total_score, dev

def generate_audit_artifact(pair, stats):
    """Створення файлу верифікації для кожної перевірки (Compliance)"""
    file_path = os.path.join(ARTIFACTS_DIR, f"audit_{pair}_{int(time.time())}.json")
    artifact = {
        "agent": "MAITS_SCANNER_v2.2",
        "timestamp": int(time.time()),
        "pair": pair,
        "metrics": stats,
        "status": "VERIFIED"
    }
    try:
        with open(file_path, 'w') as f:
            json.dump(artifact, f, indent=4)
    except Exception as e:
        print(f"⚠️ Artifact error for {pair}: {e}")

def get_historical_stats(pair="SOLUSD"):
    """
    Головна функція сканера. 
    Повертає словник з метриками та класифікацією режиму (Gear).
    """
    kraken_path = shutil.which("kraken") or "/home/ubuntu/.cargo/bin/kraken"
    
    try:
        # Отримуємо OHLC дані (60хв інтервал)
        result = subprocess.run([kraken_path, "ohlc", pair, "--interval", "60", "-o", "json"], 
                                capture_output=True, text=True)
        if result.returncode != 0:
            return None
        
        raw_data = json.loads(result.stdout)
        
        # Пошук правильного ключа в JSON відповіді Кракена
        pair_key = None
        for k in raw_data.keys():
            if k != 'last' and isinstance(raw_data[k], list):
                pair_key = k
                break
        
        if not pair_key or not raw_data[pair_key]:
            return None
            
        all_candles = raw_data[pair_key]
        closes = [float(c[4]) for c in all_candles]
        
        if len(closes) < 20:
            return None
            
        current_price = closes[-1]
        current_rsi = calculate_rsi(closes)

        # AI Аналіз та створення артефакту
        ai_sig, ai_score, dev = get_composite_signal(closes, current_rsi)
        
        stats_for_audit = {
            "price": current_price, 
            "rsi": round(current_rsi, 2), 
            "ai_signal": ai_sig,
            "dev_from_mean": round(dev, 2)
        }
        generate_audit_artifact(pair, stats_for_audit)

        # --- КЛАСИФІКАЦІЯ РЕЖИМІВ (6 GEARS) ---
        change = (closes[-1] - closes[-20]) / closes[-20] * 100
        # Амплітуда (High-Low) за останні 20 свічок
        amp = (max(closes[-20:]) - min(closes[-20:])) / min(closes[-20:]) * 100

        # 1. Пріоритет - Крах ринку
        if change <= -5.0:
            reg = "6. CRASH"
        # 2. Висока волатильність (Шторм)
        elif amp >= 5.0:
            reg = "5. HOLD"
        # 3. Режим PIG (Стрибки в межах коридору)
        elif 3.0 <= amp < 5.0 and abs(change) < 1.5:
            reg = "4. PIG"
        # 4. Виражений ріст
        elif change >= 1.5:
            reg = "2. BULLISH"
        # 5. Виражене падіння
        elif change <= -1.5:
            reg = "3. BEARISH"
        # 6. Спокійний боковик
        else:
            reg = "1. SIDEWAYS"

        return {
            "pair": pair,
            "regime": reg, 
            "price": current_price, 
            "volatility": round(amp, 2), 
            "rsi": round(current_rsi, 2),
            "ai_signal": ai_sig,
            "change_20p": round(change, 2)
        }
    except Exception as e:
        print(f"⚠️ Scanner logic error for {pair}: {e}")
        return None

if __name__ == "__main__":
    # Діагностика (запуск: python3 core/scanner.py)
    print(f"🚀 MAITS SCANNER DIAGNOSTICS | ASSETS: {len(MARKET_ASSETS)} | GEARS: 6")
    print("-" * 85)
    for p in MARKET_ASSETS[:10]: # Тестуємо перші 10
        res = get_historical_stats(p)
        if res:
            print(f"✅ {p:<8} | Vol: {res['volatility']:>5}% | RSI: {res['rsi']:>5} | AI: {res['ai_signal']:<12} | {res['regime']}")
    print("-" * 85)
    print(f"📁 Verification artifacts: {ARTIFACTS_DIR}")
