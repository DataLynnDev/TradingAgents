## Datalynn TradingAgent

The base of our framework follows a skeleton code that acts as an trading agent. Utilizing LLM powered agents and real time online external resources, the platform collaboratively evaluates the market conditions and informs the agents within the framework with the necessary data to generate an investment report.

### Main features
- Faster trade decisions based on 24/7 market monitoring
- Balanced risk assessments tailored to your investment profile
- Reduced manual workload — actionable recommendations summarized

Below is the general work flow on how the agent works at its base
<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

The pipeline works as multiple teams, below is a quick explanation on what each team and its agents does within the pipeline.

### Analyst Team
- Fundamentals Analyst: Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.
- Sentiment Analyst: Analyzes social media and public sentiment using sentiment scoring algorithms to gauge short-term market mood.
- News Analyst: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- Technical Analyst: Utilizes technical indicators (like MACD and RSI) to detect trading patterns and forecast price movements.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team
- Comprises both bullish and bearish researchers who critically assess the insights provided by the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent
- Composes reports from the analysts and researchers to make informed trading decisions. It determines the timing and magnitude of trades based on comprehensive market insights.

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager
- Continuously evaluates portfolio risk by assessing market volatility, liquidity, and other risk factors. The risk management team evaluates and adjusts trading strategies, providing assessment reports to the Portfolio Manager for final decision.
- The Portfolio Manager approves/rejects the transaction proposal. If approved, the order will be sent to the simulated exchange and executed.

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Program Structure
```bash
TradingAgents/
├── tradingagents/                
│   ├── agents/                   # Trading agent implementations
│   │   ├── analysts/             # Market analysis agents
│   │   │   ├── fundamentals_analyst.py
│   │   │   ├── market_analyst.py
│   │   │   ├── news_analyst.py
│   │   │   └── social_analyst.py
│   │   ├── managers/             # Management and coordination agents
│   │   │   ├── document_embedding.py
│   │   │   ├── quality_manager.py
│   │   │   ├── research_manager.py
│   │   │   └── risk_manager.py
│   │   ├── researchers/          # Research and debate agents
│   │   │   ├── bear_researcher.py
│   │   │   └── bull_researcher.py
│   │   ├── risk_mgmt/            # Risk management agents
│   │   │   ├── aggresive_debator.py
│   │   │   ├── conservative_debator.py
│   │   │   └── neutral_debator.py
│   │   ├── trader/               # Trading agent 
│   │   │   ├── strategies/       # Trading strategy implementations  
│   │   │   └── trader.py
│   │   └── utils/                # Agent utilities and shared components
│   │       ├── agent_states.py
│   │       ├── agent_utils.py
│   │       └── memory.py
│   ├── dataflows/                # Data processing and interfaces
│   │   ├── data_cache/           # Cached data storage
│   │   ├── config.py
│   │   ├── finnhub_utils.py
│   │   └── interface.py
│   ├── graph/                    # Workflow orchestration
│   │   ├── conditional_logic.py  # Graph traversal conditions
│   │   ├── propagation.py        # Wokrflow state initialization 
│   │   ├── reflection.py         # Agent reflection 
│   │   ├── setup.py              # Graph setup
│   │   ├── signal_processing.py
│   │   └── trading_graph.py      # Graph initialization
│   ├── __init__.py
│   └── default_config.py
├── cli/                          # Command-line interface
│   ├── static/                   # CLI static assets
│   ├── __init__.py
│   ├── main.py                   # CLI entry point
│   └── models.py
├── results/                      # Analysis results and reports
│   └── APPLE/                    # Company-specific results
│       └── 2025-*/               # Date-specific analysis
│           ├── message_tool.log
│           └── reports/          # Generated markdown reports
├── assets/                       # Static assets and images
│   ├── cli/                      # CLI-specific assets
│   ├── analyst.png
│   ├── researcher.png
│   └── example.png
├── archive/                      # Archived documentation
├── main.py                       # Main application entry point
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── uv.lock                       # Locked dependency versions
├── setup.py                      # Package setup configuration
├── README.md                    
└── LICENSE                      
```
### Current Features
-Backtesting with real time data for analysis 
-Document saving into vector databases for embedding search
-Dynamic metrics for strategies

### Key Files
```bash 
-tradingagents/graph/setup.py
-tradingagents/graph/conditional_logic.py
-tradingagents/graph/propagation.py
-tradingagents/agents/trader
-tradingagents/agents/managers
```

### Issues
-Metrics returned by agent gives back key errors when inserting metrics into backtest simulation

### Setup
Clone the repository and install requirements
```bash
git clone https://github.com/DataLynnDev/TradingAgents
cd TradingAgents
pip install -r requirements.txt
```
Set environmental variables for Finnhub and OpenAI API keys
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

You will need the OpenAI API for all the agents.
```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

### Running the Application
1. Start Milvus and Redis

```bash
#Docker installation Script 
Invoke-WebRequest https://raw.githubusercontent.com/milvus-io/milvus/refs/heads/master/scripts/standalone_embed.bat -OutFile standalone.bat

#Start the docker container
standalone.bat start

#Start Redis
docker run -d --name redis -p 6379:6379 redis:latest
```

Linux
```bash
#Docker installation script
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

#Start the Docker container
bash standalone_embed.sh start

#Start Redis
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

2. Run the application
```bash
venv/scripts/activate
python -m cli.main
```
