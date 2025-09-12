# import backtrader as bt
# import pandas as pd
# import json
# import io
# from langchain_core.tools import tool
# from tradingagents.agents.trader.strategies.indicators import (
#     AverageVolatility,
#     RecentHigh,
#     DiffHighLow,
# )

# class RiskAverseBacktest(bt.Strategy):
#     """
#     The strategy is designed to buy stocks that exhibit low volatility, have recently made new highs,
#     have high trading volume, and show a small difference between their high and low prices over a specified period.
#     The strategy exits positions if multiple conditions indicate that the favorable conditions no longer hold. This
#     strategy aims to capitalize on stocks that are stable, have upward momentum, and are actively traded.
#     """
    
#     params = dict(
#         volatility_period=20,
#         high_low_period=60,
#         vol_period=5,
#         volatility_threshold=8,
#         high_low_threshold=0.3,
#     ) 

#     def __init__(self):

#         self.candle_volatility = AverageVolatility(
#             self.data, period=self.params.volatility_period
#         )
#         self.has_new_high = RecentHigh(self.data)
#         self.past_vol = bt.indicators.SimpleMovingAverage(
#             self.data.volume, period=self.params.vol_period
#         )
#         self.diff_high_low = DiffHighLow(self.data, period=self.params.high_low_period)
#         self.data_log = []


#     def next(self):
#         # Conditions
#         cond_1 = (
#             self.candle_volatility.avg_volatility[0] < self.params.volatility_threshold
#         )
#         cond_2 = self.has_new_high.new_high[0] > 0
#         cond_3 = self.past_vol[0] > 100 * 1000
#         cond_4 = self.diff_high_low.diff[0] < self.params.high_low_threshold

#         # Combined signals
#         conditions = [cond_1, cond_2, cond_3, cond_4]
#         buy_signal = all(conditions)
#         close_signal = sum(not cond for cond in conditions) >= 2

#         # Execute trades based on signals
#         if self.position:
#             if close_signal:
#                 self.close()
#         elif buy_signal:
#             self.buy()

#         self.data_log.append({
#             "date": self.datas[0].datetime.date(0).isoformat(),
#             "close": self.datas[0].close[0],
#             "cash": self.broker.getcash(),
#             "value": self.broker.getvalue(),
#             "position_size": self.position.size,
#             "volatility": self.candle_volatility.avg_volatility[0],
#             "new_high": self.has_new_high.new_high[0],
#             "volume": self.past_vol[0],
#             "high_low_diff": self.diff_high_low.diff[0],
#         })

# @tool
# def run_backtest(csv_data) -> str:
#     """
#     Runs a backtest on the given CSV stock data string using the RiskAverseBacktest strategy.
#     Returns a summary of the final portfolio value and recent trade logs.
#     """
#     try:

#         if not csv_data or csv_data.strip() == "":
#             return "Error: No CSV data provided"

#         df = pd.read_csv(io.StringIO(csv_data), comment='#', parse_dates=['Date'])
        
#         # check if the data is enough for the backtest
#         if len(df) < 60:
#             return f"Error: Insufficient data for backtest. Need at least 60 data points, got {len(df)}"
        
#         required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
#         missing_columns = [col for col in required_columns if col not in df.columns]
#         if missing_columns:
#             return f"Error: Missing required columns: {missing_columns}"
        
#         df.set_index('Date', inplace=True)
        
#         cerebro = bt.Cerebro()
#         data = bt.feeds.PandasData(dataname=df)
#         cerebro.adddata(data)
#         cerebro.addstrategy(RiskAverseBacktest)
#         final = cerebro.run()
        
#         if not final or len(final) == 0:
#             return "Error: Backtest failed to run"
#         logs = final[0].data_log[-5:] if hasattr(final[0], 'data_log') and final[0].data_log else []
#         jsonLog = json.dumps(logs, indent=2)
        
#         return f"RiskAverseBacktest Strategy Results:\nfinal logs: {jsonLog}"
        
#     except Exception as e:
#         return f"Error during backtest: {str(e)}"