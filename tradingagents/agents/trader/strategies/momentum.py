import backtrader as bt
from langchain_core.tools import tool
from datetime import datetime
import pandas as pd
import json
import numpy as np
import io

class MomentumBacktest(bt.Strategy):
        
    params = dict(sma_period=50, momentum_period=14)
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        self.momentum = bt.indicators.Momentum(
            self.data.close, period=self.params.momentum_period
        )
        self.buy_signal = self.momentum > 0
        self.sell_signal = self.momentum < 0 
        self.close_signal = self.data.close < self.sma
        self.data_log = []

    def next(self):
        self.data_log.append({
            "date": self.datas[0].datetime.date(0).isoformat(),
            "close": self.datas[0].close[0],
            "cash": self.broker.getcash(),
            "value": self.broker.getvalue(),       
            "position_size": self.position.size, 
            "momentum": self.momentum[0],
        })  
        if self.position.size == 0:
            if self.buy_signal[0]:
                self.buy()   
            elif self.sell_signal[0]:
                self.sell()  
        elif self.position.size > 0:  
            if self.close_signal[0] or self.sell_signal[0]:
                self.close()  
        elif self.position.size < 0:  
            if self.close_signal[0] or self.buy_signal[0]:
                self.close()  

            




def run_backtest(stock_data,params) -> str:
    """
    Runs a backtest on the given CSV stock data string using the MomentumBacktest strategy.
    Returns a summary of the final portfolio value and recent trade logs.
    """
    df = pd.read_csv(io.StringIO(stock_data), comment='#', parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    
    results = []
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MomentumBacktest,**params)
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    final =  cerebro.run()   
    logs = final[0].data_log
    returns = final[0].analyzers.returns.get_analysis()
    jsonLog = json.dumps(logs, indent=2)
    results.append(jsonLog)
    results.append(returns['rtot'])
    return results

