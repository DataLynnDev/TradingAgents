import sys
from pathlib import Path
from tradingagents.agents.trader.trader import Trader 

def get_tools():
    return [Trader.run_backtest]

