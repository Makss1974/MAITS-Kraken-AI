import json
import os
from datetime import datetime

# --- КОНФІГУРАЦІЯ ШЛЯХІВ ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Шлях до логів згідно з правилами 2026-02-12 та структурою KRAKEN_PROD
LOG_PATH = os.path.join(BASE_DIR, "state/trades_history.lsonl")

def perform_final_audit(log_file=None):
    """Функція для виклику з main.py"""
    path = log_file if log_file else LOG_PATH
    return analyze_performance(path)

def analyze_performance(path=LOG_PATH):
    if not os.path.exists(path):
        print(f"📂 Логів за адресою {path} поки немає. Чекаємо перших угод...")
        return

    trades = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    trades.append(json.loads(line))
    except Exception as e:
        print(f"⚠️ Помилка читання логів: {e}")
        return

    if not trades:
        print("📉 Файл логів порожній. Аналіз відкладено.")
        return

    total_profit = 0
    wins = 0
    losses = 0
    
    # Розрахунок Max Drawdown (Peak-to-Valley)
    current_balance = 100.0 # Базис 100%
    peak = 100.0
    max_drawdown = 0.0

    for t in trades:
        p = float(t.get('profit_pct', 0))
        total_profit += p
        
        # Оновлюємо баланс для MDD
        current_balance += p
        if current_balance > peak:
            peak = current_balance
        
        drawdown = (current_balance - peak)
        if drawdown < max_drawdown:
            max_drawdown = drawdown
        
        if p > 0: wins += 1
        else: losses += 1

    print(f"\n{'='*45}")
    print(f"📈 MAITS PERFORMANCE REPORT | {datetime.now().strftime('%H:%M')}")
    print(f"{'='*45}")
    print(f"✅ Всього угод:     {len(trades)}")
    print(f"💰 Загальний профіт: {total_profit:+.2f}%")
    print(f"🏆 Win Rate:        {(wins/len(trades)*100):.1f}%")
    print(f"📉 Max Drawdown:    {max_drawdown:.2f}%")
    print(f"{'='*45}")

    # Виклик AI-інсайтів
    generate_ai_insight(total_profit, max_drawdown, len(trades))

def generate_ai_insight(profit, drawdown, count):
    """AI Аналітика на основі отриманих метрик"""
    print("\n🛡️ AI GUARDIAN INSIGHT:")
    
    if count < 5:
        print(">>> [WAIT] Мало даних. Продовжую спостереження за ринком.")
        return

    if profit > 2.0 and drawdown > -3.0:
        print(">>> [OPTIMAL] Система працює ідеально. Ризики під контролем.")
    elif drawdown < -7.0:
        print(">>> [DANGER] Критична просадка! Перевірте роботу Anti-Crash модуля.")
    elif profit < 0 and count > 10:
        print(">>> [ADVISE] Негативний тренд. Можливо, варто змінити таймфрейм сканера.")
    else:
        print(">>> [STABLE] Робота в межах норми. Коригування не потрібне.")

if __name__ == "__main__":
    # Тестовий запуск для перевірки
    analyze_performance()