import json
import os
from datetime import datetime

# --- СИНХРОНІЗАЦІЯ ШЛЯХІВ (Rule 2026-02-12) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "state/trades_history.lsonl")
REPORT_PATH = os.path.join(BASE_DIR, "state/analysis/reports/ai_insights.txt")

# --- ДОДАНА ФУНКЦІЯ ДЛЯ СУМІСНОСТІ З MAIN.PY ---
def perform_final_audit(log_file=None):
    """
    Цю функцію викликає main.py. 
    Вона запускає твій розширений аналіз.
    """
    path = log_file if log_file else LOG_PATH
    print(f"🕵️ AI Guardian завантажує звіт...")
    return analyze_performance(path)

def analyze_performance(path):
    """
    Обгортка для виклику твоєї логіки рекомендацій
    """
    report = get_ai_recommendation("DAILY")
    print(report)

# --- ТВІЙ ОРИГІНАЛЬНИЙ КОД (БЕЗ ЗМІН ЛОГІКИ) ---
def get_ai_recommendation(trigger_type="DAILY"):
    """
    Аналізує останні угоди та видає стратегічні вказівки.
    """
    if not os.path.exists(LOG_PATH):
        return "⚠️ [AI GUARDIAN] Недостатньо даних (лог-файл відсутній)."

    trades = []
    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    trades.append(json.loads(line))
    except Exception as e:
        return f"⚠️ [AI ERROR] Помилка читання логів: {e}"

    if not trades:
        return "⏳ [AI GUARDIAN] Портфель порожній. Чекаю перших сигналів від Scanner."

    # Аналіз останнього вікна угод (Context Window)
    last_window = trades[-5:]
    avg_profit = sum(float(t.get('profit_pct', 0)) for t in last_window) / len(last_window)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"--- 🤖 AI GUARDIAN REPORT | {timestamp} | [{trigger_type}] ---"
    
    if trigger_type == "INCIDENT":
        prompt = "🚨 ALERT: ВИЯВЛЕНО КРИТИЧНУ ПРОСАДКУ (MDD)."
        advice = ("📉 ACTION: Знизити Volume на 50%. "
                  "Перевірити Historian на аномальну тривалість тренду.")
    else:
        prompt = "📅 SCHEDULED: ЩОДЕННИЙ ТЕХНІЧНИЙ ОГЛЯД."
        if avg_profit > 0.5:
            advice = "✅ STATUS: Ефективність висока. BULLISH сценарій підтверджено."
        elif avg_profit < -1.0:
            advice = "⚠️ STATUS: Корекція. Рекомендую змінити RSI поріг входу на < 30."
        else:
            advice = "⏳ STATUS: Стабільно. SIDEWAYS режим домінує."

    report = (f"{header}\n{prompt}\n{advice}\n"
              f"Performance (Last 5): {avg_profit:+.2f}%\n"
              f"{'-'*45}\n")
    
    save_ai_report(report)
    return report

def save_ai_report(report):
    """Зберігає звіт у файл звітності (Rule 2026-02-12)"""
    try:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "a") as f:
            f.write(f"\n{report}")
    except Exception as e:
        print(f"❌ Не вдалося зберегти звіт: {e}")

if __name__ == "__main__":
    # Тестовий виклик
    print(get_ai_recommendation("DAILY"))