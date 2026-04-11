import json
import os
from datetime import datetime

# --- CONFIGURATION (Rule 2026-02-12) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "state/trades_history.lsonl")
REPORT_PATH = os.path.join(BASE_DIR, "state/analysis/reports/ai_insights.txt")

def perform_final_audit(log_file=None):
    """Primary entry point for main.py"""
    path = log_file if log_file else LOG_PATH
    return run_full_analysis(path)

def run_full_analysis(path):
    """Full cycle: Metrics calculation + AI Insights generation"""
    if not os.path.exists(path):
        print(f"📂 [AI GUARDIAN] No logs found. Waiting for data...")
        return

    trades = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line: trades.append(json.loads(line))
    except Exception as e:
        print(f"⚠️ [AI ERROR] Log read error: {e}")
        return

    if not trades:
        print("📉 [AI GUARDIAN] Log is empty. Analysis postponed.")
        return

    # --- 1. MATHEMATICAL BLOCK ---
    stats = calculate_performance_metrics(trades)
    
    # Console Report Output
    print(f"\n{'='*45}")
    print(f"📈 MAITS PERFORMANCE REPORT | {datetime.now().strftime('%H:%M')}")
    print(f"{'='*45}")
    print(f"✅ Total Trades:     {stats['count']}")
    print(f"💰 Total Profit:    {stats['profit']:+.2f}%")
    print(f"🏆 Win Rate:         {stats['win_rate']:.1f}%")
    print(f"📉 Max Drawdown:    {stats['mdd']:.2f}%")
    print(f"{'='*45}")

    # --- 2. STRATEGIC BLOCK (AI Insights) ---
    insight = generate_ai_insight(stats)
    print(f"\n🛡️ AI GUARDIAN INSIGHT:\n>>> {insight}")
    
    # Save report to file
    save_ai_report(stats, insight)

def calculate_performance_metrics(trades):
    """Calculates MDD, WinRate, and Cumulative Profit"""
    total_profit = 0
    wins = 0
    current_balance = 100.0
    peak = 100.0
    max_drawdown = 0.0

    for t in trades:
        # Support for multiple key formats (pnl or profit_pct)
        p = float(t.get('pnl', t.get('profit_pct', 0)))
        total_profit += p
        
        current_balance += p
        if current_balance > peak: peak = current_balance
        
        drawdown = current_balance - peak
        if drawdown < max_drawdown: max_drawdown = drawdown
        
        if p > 0: wins += 1

    return {
        "count": len(trades),
        "profit": total_profit,
        "win_rate": (wins / len(trades) * 100) if trades else 0,
        "mdd": max_drawdown,
        "last_pnl": float(trades[-1].get('pnl', trades[-1].get('profit_pct', 0))) if trades else 0
    }

def generate_ai_insight(stats):
    """Logic-based advice generation based on performance data"""
    if stats['count'] < 5:
        return "[WAIT] Insufficient data for conclusions. Monitoring market behavior."

    if stats['mdd'] < -7.0:
        return "[DANGER] Critical drawdown detected! Immediate Gearbox limit reduction advised."
    
    if stats['profit'] > 2.0 and stats['mdd'] > -3.0:
        return "[OPTIMAL] System stable. Market trend confirmed. Optimal performance."
    
    if stats['last_pnl'] < -1.0:
        return "[ADVISE] Local correction detected. Recommend reviewing RSI thresholds."
    
    return "[STABLE] Normal operation. No immediate parameter adjustment required."

def save_ai_report(stats, insight):
    """Saves report to ai_insights.txt (Rule 2026-02-12)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = (f"[{timestamp}] Trades: {stats['count']} | PnL: {stats['profit']:+.2f}% | "
              f"MDD: {stats['mdd']:.2f}% | Insight: {insight}\n")
    try:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "a") as f:
            f.write(report)
    except Exception as e:
        print(f"❌ Report write error: {e}")

if __name__ == "__main__":
    run_full_analysis(LOG_PATH)
