from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import redis
import time
import json
import functools
from . import strategies
from datetime import datetime, timedelta
'''
decision log - each report needs a log of all decisions made, right now focusing on trader (FOCUS)
-how to store data? how do we store the decision logs
backtest (FOCUS)
-how to store the results? 
-how do i determine the results are good? what metrics are key? where in the strategies are affecting the results? want always up

need to make be more specific on the metrics on the backtest, how is data stored? how will it be used? 
-store yfin data? 
-store metric data how?


历史记录 decision log 该如何存入数据库
我们最终的metric指标该如何确定，和评估


create a document that not just talks about the general pipeline, but also how will the data be used, stored, the metrics involved, etc.


chill on strategies for now, other side are doing it

analysts
-do we save the metrics a a structured db?

how should the workflow go 
number of trades done 
ROI
how long did it take to run

'''
class Trader:
    instance = None  
    def __init__(self,llm,memory,toolkit,strategy): 
        self.llm = llm
        self.memory = memory
        self.toolkit = toolkit
        self.strategy = strategy
        self.run_backtest_func = None
        self.state = None
        self.params = None
        Trader.instance = self
    
    @staticmethod
    @tool
    def run_backtest(stock_data: str):
        """
        Runs a backtest on the given CSV stock data string using a selected strategy.
        Returns a summary of the final portfolio value and recent trade logs.
        """
        return Trader.instance.backtest(stock_data)
    
    
    #TO FIX:
    #PARSE RETRURN STRING FROM MODEL AS ACTUAL JSON TO PARAMS
    #NO LOOP CURRENTLY, WILL ADD UNTIL FIX
    def backtest(self, stock_data):
        """
        Runs a backtest on the given CSV stock data string using a selected strategy.
        Returns a summary of the final portfolio value and recent trade logs.
        """
        curr_gain = 0;
        curr_log = "";
        
        system_message = """You are a quantitative parameter optimization expert. Your goal is to improve trading strategy performance through systematic parameter adjustment.

        OPTIMIZATION FRAMEWORK:
        1. RISK-ADJUSTED RETURNS: Prioritize Sharpe ratio > raw returns
        2. DRAWDOWN CONTROL: Maximum drawdown should decrease
        3. WIN RATE vs PROFIT FACTOR: Balance frequency vs magnitude
        4. MARKET REGIME ADAPTATION: Parameters should work across conditions

        PARAMETER ADJUSTMENT LOGIC:
        - If excessive whipsaws → Increase signal smoothing periods
        - If missing trends → Decrease lag in indicators  
        - If large drawdowns → Tighten stop-loss, widen take-profit
        - If low win rate → Adjust entry thresholds for higher quality signals
        - If high win rate but low profits → Reduce position sizing constraints

        EVALUATION METRICS HIERARCHY:
        1. Sharpe Ratio (target: >1.5)
        2. Maximum Drawdown (target: <10%)
        3. Profit Factor (target: >1.3)
        4. Win Rate (target: 55-70%)
        5. Average Trade Duration (market-dependent)

        RESPONSE FORMAT: JSON only with numeric values
        Example: {"sma_period": 15, "rsi_threshold": 25, "stop_loss_pct": 0.02}"""
        
        # Use current params for initial backtest
        params = self.params
        for _ in range(2):
            backtest_logs = self.run_backtest_func(stock_data, params)
            
            compare_message = ""
            if curr_log:
                compare_message = f"""BENCHMARK COMPARISON:
                Current best performance metrics: {curr_log}
                Target: Match or exceed these results while reducing risk.
                Focus on parameters that improved: Sharpe ratio, reduced drawdown, or higher profit factor."""

            param_names = ", ".join([f'"{k}": {v}' for k, v in params.items()])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"{system_message}\n\n{compare_message}"),
                ("user", 
                "BACKTEST ANALYSIS:\n{backtest}\n\n"
                "CURRENT PARAMETERS: {{{param_names}}}\n\n"
                "OPTIMIZATION TASK:\n"
                "1. Identify performance bottlenecks from logs\n"
                "2. Determine which parameters caused poor trades\n" 
                "3. Return ONLY the parameters you want to change\n"
                "CONSTRAINTS:\n"
                "- Change parameters by 10-30% increments only\n"
                "- Maintain parameter relationships (e.g., fast MA < slow MA)\n"
                "- Consider market volatility in current period\n"
                "- Only return parameters that exist in current parameters\n\n"
                "Return ONLY this exact format: {{\"param_name\": value}}\n"
                "DO NOT GIVE ANY EXPLANATIONS\n" )
            ])
            prompt = prompt.partial(compare_message=compare_message)
            prompt = prompt.partial(backtest=backtest_logs[0])
            prompt = prompt.partial(param_names=param_names)
            formatted_prompt = prompt.format_prompt() 
            result = self.llm.invoke(formatted_prompt)
            response = result.content.strip()
            
            try:
                config_dict = json.loads(response)
                if backtest_logs[1] > curr_gain:
                    curr_gain = backtest_logs[1]
                    curr_log = backtest_logs[0]
                    params.update(config_dict)
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error: {e}")
                pass
                
        final_log = curr_log
        return final_log
    def create_trader(self):
        def trader_node(state, name):
            #r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            self.state = state
            company_name = state["company_of_interest"]
            investment_plan = state["investment_plan"]
            market_research_report = state["market_report"]
            sentiment_report = state["sentiment_report"]
            news_report = state["news_report"]
            fundamentals_report = state["fundamentals_report"]

            rewrite_plan = state["rewrite"]
            
            curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
            past_memories = self.memory.get_memories(curr_situation, n_matches=2)
            
            current_date = state["trade_date"]
            ticker = state["company_of_interest"]
            strategy_module = getattr(strategies, self.strategy) 
            strategy_Obj = getattr(strategy_module,'MomentumBacktest',None)
            self.params = dict(strategy_Obj.params._getitems())
            
            past_memory_str = ""
            if past_memories:
                for i, rec in enumerate(past_memories, 1):
                    past_memory_str += rec["recommendation"] + "\n\n"
            else:
                past_memory_str = "No past memories found."
            

            run_backtest_func = getattr(strategy_module, 'run_backtest', None)
            if not run_backtest_func:
                raise ValueError(f"Strategy {self.strategy} does not have a run_backtest function")
            else:
                self.run_backtest_func = run_backtest_func
            
            
            tools = [
                self.toolkit.get_YFin_data_online,
                self.run_backtest
            ]
            
                       
            report_structure = """THE REPORT MUST FOLLOW THIS EXACT STRUCTURE:
            
            DATE RANGE
            - Date range in MM-DD-YYYY format (3 months historical)

            MARKET CONTEXT ANALYSIS
            - Current market regime (bull/bear/sideways trend)
            - Sector performance vs S&P 500
            - Key economic events in analysis period
            - Market volatility level (VIX reference)

            HISTORICAL PERFORMANCE AND TECHNICAL ANALYSIS
            - Opening/closing prices with percentage change
            - Highest/lowest prices with support/resistance levels
            - Price trend with specific moving average positions
            - Volume analysis and momentum indicators
            - Key technical breakouts/breakdowns with dates

            BACKTEST RESULTS AND DECISION LOG
            - Strategy name and configuration used
            - Complete chronological decision history with dates
            - Entry/exit signals with indicator values (RSI, MACD, etc.)
            - Trade outcomes: wins/losses with percentages
            - Drawdown periods and recovery analysis
            - Strategy performance metrics (Sharpe ratio, max drawdown)

            RISK ASSESSMENT AND VALIDATION
            - Strategy Sharpe ratio (minimum 1.0 required for BUY)
            - Historical win rate % (minimum 60% for aggressive positions)
            - Maximum consecutive losses observed
            - Current volatility vs historical average
            - Correlation risk with portfolio/market
            - Upcoming earnings/events within 30 days

            POSITION SIZING AND RISK MANAGEMENT
            - Recommended position size (% of portfolio)
            - Entry price level with precision
            - Stop-loss level (maximum 2% portfolio risk)
            - Take-profit targets (minimum 1:2 risk-reward)
            - Maximum holding period
            - Position invalidation criteria

            FINAL RECOMMENDATION
            - Decision: BUY/SELL/HOLD with confidence %
            - Risk-adjusted justification
            - Specific action plan with price levels
            - Portfolio impact assessment
            """

            system_message = """You are a risk-first trading agent. Execute this sequence:

            MANDATORY STEPS:
            1. Call stock data retrieval tool for {ticker} (3 months historical)
            2. Verify data completeness - retry if insufficient
            3. Call run_backtest tool with retrieved data
            4. Analyze backtest performance against minimum thresholds

            DECISION FRAMEWORK HIERARCHY:
            1. RISK MANAGEMENT OVERRIDES ALL SIGNALS
            2. Market context must confirm technical signals  
            3. Strategy must meet minimum performance thresholds:
            - Sharpe ratio ≥ 1.0 for BUY recommendations
            - Win rate ≥ 60% for position size >5% portfolio
            - Max drawdown ≤ 15% for strategy validation
            4. Position sizing based on: confidence × (1/volatility)

            CRITICAL CONSTRAINTS:
            - Maximum position size: 10% of portfolio
            - Stop-loss mandatory: 2% portfolio risk maximum
            - No positions during high volatility periods (VIX >30)
            - No trades 3 days before/after earnings unless specified
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", 
                "You are analyzing {ticker} for {company_name} with current date {current_date}.\n\n"
                "INVESTMENT CONTEXT:\n{investment_plan}\n\n"
                "RISK MANAGEMENT PRIORITY: All recommendations must prioritize capital preservation.\n"
                "Use tools in sequence: {tool_names}\n\n"
                "HISTORICAL CONTEXT: {past_memory_str}\n"
                "Learn from past mistakes - if previous similar setups failed, adjust risk accordingly.\n\n"
                "{system_message}\n\n"
                "REPORT STRUCTURE:\n{report_structure}"),
                
                ("user", 
                "Execute comprehensive analysis for {ticker}:\n\n"
                "MANDATORY REQUIREMENTS:\n"
                "1. Risk assessment BEFORE any buy/sell recommendation\n"
                "2. Specific price levels for entry/exit/stop-loss\n"
                "3. Position size as % of portfolio\n"
                "4. Maximum holding period definition\n\n"
                "FINAL OUTPUT MUST END WITH:\n"
                "'FINAL TRANSACTION PROPOSAL: **BUY/SELL/HOLD [X%]** at $[price] | Stop: $[price] | Target: $[price] | Risk: [X%] portfolio | Max Hold: [X] days'\n\n"
                "If HOLD: specify review date and conditions for position change."
                "{rewrite}"),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            rewrite = "This is a rewritten version of the plan as the report generated earlier was not feasible, you MUST use this to generate a better report. {rewrite_plan}" if rewrite_plan else ""
            
            prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
            prompt = prompt.partial(system_message=system_message)
            prompt = prompt.partial(current_date=current_date)
            prompt = prompt.partial(ticker=ticker)
            prompt = prompt.partial(company_name = company_name)
            prompt = prompt.partial(investment_plan=investment_plan)
            prompt = prompt.partial(past_memory_str= past_memory_str)
            prompt = prompt.partial(report_structure = report_structure)
            prompt = prompt.partial(rewrite=rewrite)
            new_chain = prompt | self.llm.bind_tools(tools)

            final_result = new_chain.invoke(state["messages"])
            final_report = ""

            final_report = final_result.content if final_result.content else "Processing analysis..."
            #do stuff with htis final report, what metrics can we get from this?
            
            return {
                "messages": [final_result],
                "trader_investment_plan":final_report,
                "sender": name,
            }
        return functools.partial(trader_node, name="Trader")