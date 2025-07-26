import backtrader as bt
from langchain_core.tools import tool
from datetime import datetime
import pandas as pd
import json
import io
class BBandsBacktest(bt.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2.0),
    )

    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(
            self.datas[0].close, period=self.p.period, devfactor=self.p.devfactor
        )
        self.data_log = []

    def next(self):
        self.data_log.append({
            "date": self.datas[0].datetime.date(0).isoformat(),
            "close": self.datas[0].close[0],
            "cash": self.broker.getcash(),
            "value": self.broker.getvalue(),
            "position_size": self.position.size,
            "bbands_top": self.bbands.top[0],
            "bbands_mid": self.bbands.mid[0],
            "bbands_bot": self.bbands.bot[0],
        })

        if not self.position and self.datas[0].close[0] < self.bbands.bot[0]:
            self.buy()
        elif self.position and self.datas[0].close[0] > self.bbands.mid[0]:
            self.sell()
            

@tool
def run_backtest(csv_data) -> str:
    """
    Runs a backtest on the given CSV stock data string using the BbandsBacktest strategy.
    Returns a summary of the final portfolio value and recent trade logs.
    """
    df = pd.read_csv(io.StringIO(csv_data), comment='#', parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(BBandsBacktest)
    final =  cerebro.run()   
    logs = final[0].data_log[-5:]
    jsonLog = json.dumps(logs, indent=2)
    return f"final logs: {jsonLog}"