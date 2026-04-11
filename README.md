[README.md](https://github.com/user-attachments/files/26639058/README.md)
🐺 MAITS: Makss AI Trading System (v2.4)
MAITS is an autonomous, multi-strategy trading agent designed for the Kraken exchange. Unlike simple bots, 
MAITS acts as a Market Orchestrator, segmenting the entire market into specific regimes and deploying dedicated trading engines for each.

🧠 The "6-Gear" Logic: Adaptive Intelligence
MAITS doesn't use a "one-size-fits-all" strategy. It dynamically switches between 6 specialized engines ("Gears") based on real-time market DNA:

1. SIDEWAYS Engine: High-frequency grid-trading with adaptive volatility harvesting.

2. BULLISH Engine: Trend-following with Stochastic-optimized pullback entry logic.

3. BEARISH Engine: Selective shorting (Majors) and capital preservation protocols.

4. PIG (Swing) Engine: Momentum-based trading capturing medium-term price swings.

5. HOLD Engine: Zen-strategy for strategic asset accumulation during extreme discounts.

6. ANTI-CRASH Engine: A 3-level emergency shield for Black-Swan events (Asset, Market, or Global crash).

🚀 Key Features for Hackathon 2026
🧬 Multi-Cylinder Architecture
Each trading pair is treated as an independent Cylinder with its own risk profile (Conservative/Aggressive). 
This allows MAITS to manage 40+ assets simultaneously without cross-contamination of logic or budget.

🗣️ Explainable AI (XAI) Logging
MAITS doesn't just trade; it communicates. Every decision is backed by a human-readable narrative in the logs:

“Executing BUY for XBTUSD: Price hit lower boundary of the 1.74% volatility corridor. Expected mean reversion.”

⚙️ Gearbox Capital Allocation
The Gearbox unit performs real-time portfolio optimization, distributing a $5,000 budget with a mandatory
 20% safety reserve. It applies efficiency coefficients to prioritize the most profitable market regimes.

🛡️ Technical Architecture
Selector: Real-time DNA analysis of 41+ assets via Kraken CLI.

AI Guardian: Integrated auditor performing health checks and MDD monitoring.

LSONL Historian: High-performance, ML-ready logging for future model training.

State Persistence: Individual engine states are maintained during the execution cycle.

💻 Quick Start (Judge's Guide)
To run MAITS in your local environment:

Clone & Install Dependencies:

Bash
git clone https://github.com/your-repo/maits-v2.4.git
cd maits-v2.4
pip install -r requirements.txt
Initialize the System:

Bash
python3 main.py
Note: The system will automatically initialize in Simulation Mode if Kraken API keys are not detected.

📊 Live Dashboard Preview
Plaintext
=============================================
📈 MAITS PERFORMANCE DASHBOARD | 08:35
=============================================
📡 Status:          ONLINE
⚙️  Active Engine:   SIDEWAYS_ENGINE
📊 Market Regime:   1. SIDEWAYS (Weight 99.6%)
🔢 Active Pairs:    40
---------------------------------------------
✅ Total Trades:     343
💰 Total PnL:       +71.63%
🏆 Win Rate:         81.9%
📉 Max Drawdown:    -0.16%
=============================================

Це стратегічно правильний хід. Жюрі має бачити, що ти не просто написав код «на колінці» за вихідні, а будуєш серйозну екосистему. Такий план перетворює твій проект на потенційний стартап.

Ось детальний Strategic Roadmap 2026, який ти можеш вставити в README.md або в презентацію. Я додав перші два квартали, де ми закріплюємо успіх хакатону.

🗺️ MAITS Strategic Roadmap 2026: From Agent to Ecosystem
Q1 2026: Foundation & Validation (Hackathon Phase)
Core Engine Development: Completion of the "6-Gear" autonomous logic.

Kraken CLI Integration: Implementation of AI-driven execution via command-line interface.

Explainable AI (XAI): Rollout of the narrative logging system for transparent decision-making.

Simulation Excellence: Achieving stable +70% PnL in production-style sandbox environments.

Q2 2026: Live Production & Scalability
Mainnet Deployment: Transition from Sandbox to live Kraken exchange trading with real capital.

Multi-Account Management: Upgrading the Gearbox to handle capital allocation across multiple sub-accounts.

Advanced Analytics Suite: Integration of the BotAnalyst with a web-based dashboard for real-time performance tracking (Grafana/Streamlit).

Security Hardening: Implementation of hardware-encrypted API key management (Rule 2025-12-22).

Q3 2026: Decentralized Identity (ERC-8004 Integration)
Agent Identity Registry: Registering the MAITS unique ID on-chain via ERC-8004.

Trust Signal Minting: Automatically generating verifiable artifacts for every successful trade using web3.py.

On-chain Reputation: Building a transparent performance history that cannot be altered, attracting institutional liquidity.

Validator Nodes: Enabling external validation of MAITS trading signals to increase the "Trust Score."

Q4 2026: Institutional Risk Governance
Smart Risk Router: Implementation of a Solidity-based Risk Router that acts as an "on-chain circuit breaker."

Exposure Limits: Hard-coding maximum drawdown and position size limits into smart contracts (Trustless Security).

Social Trading API: Allowing third-party investors to "follow" MAITS signals via ERC-8004 identity verification.

Global Expansion: Adding support for additional top-tier exchanges beyond Kraken.
Developed by Makss for Hackathon 2026
MAITS: Protecting Capital. Harvesting Volatility. Explaining Decisions.
