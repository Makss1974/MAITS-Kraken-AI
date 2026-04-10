import subprocess
import json
import shutil
import os

# --- КОНФІГУРАЦІЯ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def calculate_probabilities(pair="XBTUSD"):
    """
    Аналізує історію циклів та обчислює ймовірність 
    завершення поточного ринкового режиму.
    """
    kraken_path = shutil.which("kraken") or "/home/ubuntu/.cargo/bin/kraken"
    
    try:
        # Отримуємо свічки (за замовчуванням 1г)
        result = subprocess.run([kraken_path, "ohlc", pair, "-o", "json"], 
                                capture_output=True, text=True)
        if result.returncode != 0:
            return 0
            
        raw_data = json.loads(result.stdout)
        
        # Пошук динамічного ключа пари
        pair_key = next((k for k in raw_data.keys() if k != 'last' and isinstance(raw_data[k], list)), None)
        if not pair_key:
            return 0
            
        candles = raw_data[pair_key]
        closes = [float(c[4]) for c in candles]
        
        if len(closes) < 50:
            return 0
        
        # 1. Рахуємо середній "шум" (волатильність) для калібрування режимів
        changes = [abs((closes[i] - closes[i-1]) / closes[i-1] * 100) for i in range(1, len(closes))]
        avg_vol = sum(changes) / len(changes)
        
        # 2. Відтворюємо історію режимів (Regime Back-tracing)
        regimes_history = []
        current_len = 0
        current_type = None
        
        # Аналізуємо вікнами по 10 періодів
        for i in range(10, len(closes)):
            change = (closes[i] - closes[i-10]) / closes[i-10] * 100
            
            # Класифікація (спрощена для історика)
            if abs(change) < avg_vol: 
                new_type = "SIDEWAYS"
            elif change > avg_vol * 2.5: 
                new_type = "BULL"
            elif change < -avg_vol * 2.5: 
                new_type = "BEAR"
            else: 
                new_type = "UNCERTAIN"
            
            if new_type == current_type:
                current_len += 1
            else:
                if current_type: 
                    regimes_history.append((current_type, current_len))
                current_type, current_len = new_type, 1
        
        # 3. Розрахунок ймовірності вичерпання (Exhaustion Probability)
        # Беремо середню тривалість такого ж типу режиму в минулому
        similar_durations = [d for t, d in regimes_history if t == current_type and t != "UNCERTAIN"]
        avg_life = sum(similar_durations) / len(similar_durations) if similar_durations else 10
        
        # Ймовірність = (поточна тривалість / середня тривалість) * 100
        # Якщо current_len перевищує середню — ймовірність розвороту стрімко зростає
        prob_end = (current_len / avg_life) * 100 if avg_life > 0 else 50
        prob_end = min(max(prob_end, 0), 100) # Обмежуємо 0-100%

        print(f"--- 📜 MAITS HISTORIAN | {pair} ---")
        print(f"Current Regime: {current_type} | Duration: {current_len}")
        print(f"Avg Life Span:  {avg_life:.1f} | Exhaustion: {prob_end:.1f}%")
        
        return round(prob_end, 2)

    except Exception as e:
        print(f"⚠️ Historian Error: {e}")
        return 0

if __name__ == "__main__":
    # Тестовий запуск
    p = calculate_probabilities("SOLUSD")
    if p > 80:
        print("🛑 WARNING: Trend is overextended. High reversal probability!")
    elif p < 30:
        print("✅ INFO: Trend is young. Potential for growth remains.")