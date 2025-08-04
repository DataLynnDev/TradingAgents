from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools
import time
import json
from . import strategies
'''
decision log - each report needs a log of all decisions made, right now focusing on trader, will need

'''
class Trader:
    def __init__(self,llm,memory,toolkit,strategy): 
        self.strategy = None
        self.llm = llm
        self.memory = memory
        self.toolkit = toolkit
        self.strategy = strategy
    def create_trader(self):
        def trader_node(state, name):
            company_name = state["company_of_interest"]
            investment_plan = state["investment_plan"]
            market_research_report = state["market_report"]
            sentiment_report = state["sentiment_report"]
            news_report = state["news_report"]
            fundamentals_report = state["fundamentals_report"]

            curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
            past_memories = self.memory.get_memories(curr_situation, n_matches=2)
            
            current_date = state["trade_date"]
            ticker = state["company_of_interest"]
            strategy_module = getattr(strategies, self.strategy) 
            
            past_memory_str = ""
            if past_memories:
                for i, rec in enumerate(past_memories, 1):
                    past_memory_str += rec["recommendation"] + "\n\n"
            else:
                past_memory_str = "No past memories found."
            
            # 获取策略模块中的 run_backtest 函数
            run_backtest_func = getattr(strategy_module, 'run_backtest', None)
            if not run_backtest_func:
                raise ValueError(f"Strategy {self.strategy} does not have a run_backtest function")
            
            tools = [
                self.toolkit.get_YFin_data_online,
                run_backtest_func
            ]
            system_message = (
                f"""You are a trading agent. Follow these steps exactly ONCE, DO NOT SKIP:
                    1. First, ALWAYS call the tool to retrieve raw stock data. If the retrieved data is empty, retrieve it until actual data comes through.
                    2. After receiving the data, IMMEDIATELY and ALWAYS call the 'run_backtest' tool for the strategy: {self.strategy},  with the stock data as input, display the strategy name and logs in the report.
                    3. Only after both tool calls are complete, analyze the backtest log as below
                    4. Analyzing the data, give the prediction probability confidence (0-100%), maximum allowable loss for a single transaction, strategy historical win rate backtest value and abnormal fluctuation warning
                    5. Provide a recommendation after. DO NOT CALL ANY MORE TOOLS AFTER
                   """
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}."
                "This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment." 
                "Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\n"
                "Furthermore, you must use the given tools, DO NOT SKIP THIS: {tool_names},{system_message}."
                "Create a report for {ticker} starting from {current_date}, GOING BACK SIX MONTHS for sufficient historical data for technical analysis, DO NOT GO INTO THE FUTURE DATES. Include the date range in the report"
                "Using the given tools, include your analysis and logs on the report"),
                ("user", "You are a trading agent analyzing market data to make investment decisions."
                "Based on your analysis, provide a specific recommendation to buy, sell, or hold. "
                "End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation."
                "If the decision is to HOLD, give the recommended holding time as well."
                "Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is the past memory: {past_memory_str}"),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
            prompt = prompt.partial(system_message=system_message)
            prompt = prompt.partial(current_date=current_date)
            prompt = prompt.partial(ticker=ticker)
            prompt = prompt.partial(company_name = company_name)
            prompt = prompt.partial(investment_plan=investment_plan)
            prompt = prompt.partial(past_memory_str= past_memory_str)
            chain = prompt | self.llm.bind_tools(tools)

            result = chain.invoke(state["messages"])
            report = ""

            report = result.content if result.content else "Processing analysis..."
            
            return {
                "messages": [result],
                "trader_investment_plan": report,
                "sender": name,
            }
        return functools.partial(trader_node, name="Trader")