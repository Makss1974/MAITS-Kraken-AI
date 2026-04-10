[README.md](https://github.com/user-attachments/files/26639058/README.md)
# 🐺 MAITS: Multi-Layer AI Trading System

MAITS is an autonomous trading agent designed for the Kraken exchange. It combines statistical analysis, trend tracking, and AI-driven risk management.

## 🧠 The Three-Stage Analysis Logic

Our strategy isn't based on luck; it’s a systematic 3-layer filter:

1.  **Stage 1: THE SELECTOR (Market Context)**
    * Scans available pairs (e.g., SOLUSD, BTCUSD).
    * Filters by 24h volume and volatility to find where the "smart money" is moving.
2.  **Stage 2: THE SCANNER (Technical DNA)**
    * Analyzes **RSI** (Relative Strength Index) to avoid buying overbought assets.
    * Uses **Bollinger Bands** to identify price breakouts and volatility squeezes.
    * Identifies the Market Regime: Bullish, Bearish, or Sideways.
3.  **Stage 3: THE HISTORIAN (Probabilistic Edge)**
    * Calculates the **Trend Exhaustion Probability**.
    * If the trend is too old (high probability of reversal), the bot stays in "WAIT" mode, even if technicals look good.

## 🛡️ AI Guardian & Risk Management
* **Automatic State Tracking:** Persistent `bot_state.json` ensures the bot never "forgets" its position after a crash.
* **AI Guardian:** An integrated monitor that triggers an AI-powered post-mortem analysis if a drawdown >15% occurs.
* **LSONL Logging:** Every trade is recorded in a machine-readable format for future ML training.
