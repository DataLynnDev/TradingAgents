import sys
from pathlib import Path
import importlib
sys.path.append(str(Path(__file__).resolve().parents[2]))

import tradingagents.agents.trader.strategies as strategies
import inspect

def get_tools(strategy):
    backtests = []
    module_name = f"tradingagents.agents.trader.strategies.{strategy}"
    module = importlib.import_module(module_name)

    backtests = []
    for name, obj in inspect.getmembers(module):
        if callable(obj) and name.lower().endswith("run_backtest"):
            backtests.append(obj)
    return backtests

