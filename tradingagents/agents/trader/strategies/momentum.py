import backtrader as bt
from langchain_core.tools import tool
from datetime import datetime
import pandas as pd
import json
import io

class MomentumBacktest(bt.Strategy):
    params = (
        ("momentum_period", 10),  
    )
    
    def __init__(self):
        self.momentum = self.datas[0].close - self.datas[0].close(-self.p.momentum_period)
        self.data_log = []
    
    def next(self):
        self.data_log.append({
            "date": self.datas[0].datetime.date(0).isoformat(),
            "close": self.datas[0].close[0],
            "cash": self.broker.getcash(),
            "value": self.broker.getvalue(),
            "position_size": self.position.size,
            "momentum": self.momentum[0] if len(self) > self.p.momentum_period else None,
        })
        if len(self) <= self.p.momentum_period:
            return

        if not self.position and self.momentum[0] > 0:
            self.buy()
        elif self.position and self.momentum[0] < 0:
            self.sell()
            
        

  

@tool
def run_backtest(csv_data) -> str:
    """
    Runs a backtest on the given CSV stock data string using the MomentumBacktest strategy.
    Returns a summary of the final portfolio value and recent trade logs.
    """
    df = pd.read_csv(io.StringIO(csv_data), comment='#', parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MomentumBacktest)
    final =  cerebro.run()   
    logs = final[0].data_log[-5:]
    jsonLog = json.dumps(logs, indent=2)
    return f"final logs: {jsonLog}"