import backtrader as bt
from langchain_core.tools import tool
from datetime import datetime
import pandas as pd
import json
import io

class MomentumBacktest(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(period=5)
        self.data_log = []

    def next(self):
        self.data_log.append({
            "date": self.datas[0].datetime.date(0).isoformat(),
            "close": self.datas[0].close[0],
            "cash": self.broker.getcash(),
            "value": self.broker.getvalue(),
            "position_size": self.position.size,
            "unrealized_pnl": self.position.pnl,
        })


@tool
def run_backtest(csv_data) -> str:
    """
    Runs a backtest on the given CSV stock data string using the MomentumBacktest strategy.
    Returns a summary of the final portfolio value and recent trade logs.
    """
    df = pd.read_csv(io.StringIO(csv_data),comment='#') 
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MomentumBacktest)
    final =  cerebro.run()   
    logs = final[0].data_log[-5:]
    jsonLog = json.dumps(logs, indent=2)
    return f"final logs: {jsonLog}"