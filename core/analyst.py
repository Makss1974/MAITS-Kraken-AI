import json
import os
from datetime import datetime

class BotAnalyst:
    def __init__(self, log_path, start_balance=10000.0):
        self.log_path = log_path
        self.start_balance = start_balance
        self.total_trades = 0
        self.total_profit = 0.0
        self.win_rate = 0.0
        self.max_drawdown = 0.0

    def _update_metrics(self):
        """Internal method to recalculate metrics from LSONL logs"""
        if not os.path.exists(self.log_path):
            return

        trades = []
        try:
            with open(self.log_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        trades.append(json.loads(line))
        except Exception:
            return

        if not trades:
            return

        self.total_trades = len(trades)
        wins = 0
        cumulative_pnl = 0.0
        peak_balance = self.start_balance
        current_balance = self.start_balance
        mdd = 0.0

        for t in trades:
            pnl = float(t.get('profit_pct', 0))
            cumulative_pnl += pnl
            current_balance *= (1 + pnl / 100)
            
            if current_balance > peak_balance:
                peak_balance = current_balance
            
            drawdown = (current_balance - peak_balance) / peak_balance * 100
            if drawdown < mdd:
                mdd = drawdown
            
            if pnl > 0:
                wins += 1

        self.total_profit = cumulative_pnl
        self.win_rate = (wins / self.total_trades) * 100
        self.max_drawdown = mdd

    def display_dashboard(self, active_engine_name, market_regime, pairs_count):
        """
        Main visualization method called by main.py.
        Fixed: Added 'pairs_count' argument to match main.py call.
        """
        self._update_metrics()

        print("\n" + "="*45)
        print(f"📈 MAITS PERFORMANCE DASHBOARD | {datetime.now().strftime('%H:%M')}")
        print("="*45)
        print(f"📡 Status:          ONLINE")
        print(f"⚙️  Active Engine:   {active_engine_name}")
        print(f"📊 Market Regime:   {market_regime}")
        print(f"🔢 Active Pairs:    {pairs_count}")
        print("-" * 45)
        print(f"✅ Total Trades:     {self.total_trades}")
        print(f"💰 Total PnL:       {self.total_profit:+.2f}%")
        print(f"🏆 Win Rate:         {self.win_rate:.1f}%")
        print(f"📉 Max Drawdown:    {self.max_drawdown:.2f}%")
        print("="*45)