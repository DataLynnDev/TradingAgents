from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools
import time
import json
from .strategies import test
'''- dynamic prompt 
metrics for the position
what does it mean?
according to the metrics, the next steps? (for the agents)

'''
class Trader:
    def __init__(self,llm,memory,toolkit):
        self.strategy = None
        self.llm = llm
        self.memory = memory
        self.toolkit = toolkit
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
            
            past_memory_str = ""
            if past_memories:
                for i, rec in enumerate(past_memories, 1):
                    past_memory_str += rec["recommendation"] + "\n\n"
            else:
                past_memory_str = "No past memories found."
            if self.toolkit.config["online_tools"]:
                tools = [
                    self.toolkit.get_YFin_data_online,
                    test.run_backtest
                ]
            else:
                tools = [
                    self.toolkit.get_YFin_data,
                    test.run_backtest
                ]
            system_message = (
                """You are a trading agent. Follow these steps exactly ONCE, DO NOT SKIP:
                    1. First, ALWAYS call the tool named 'get_YFin_data' to retrieve raw stock data. If the retrieved data is empty, retrieve it until actual data comes through.
                    2. After receiving the data, IMMEDIATELY and ALWAYS call the 'run_backtest' tool with the stock data as input, display the logs in the report.
                    3. Only after both tool calls are complete, analyze the backtest logs and provide a recommendation. DO NOT CALL ANY MORE TOOLS AFTER
                   """
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}."
                "This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment." 
                "Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\n"
                "Furthermore, you must use the given tools, DO NOT SKIP THIS: {tool_names},{system_message}."
                "Create a report for {ticker} starting from {current_date}, going back a MONTH. Include the date range in the report"
                "Using the given tools, include your analysis and logs on the report"),
                ("user", "You are a trading agent analyzing market data to make investment decisions."
                "Based on your analysis, provide a specific recommendation to buy, sell, or hold. "
                "End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation."
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

            report = result.content if result.content else "Processing momentum analysis..."

            return {
                "messages": [result],
                "trader_investment_plan": report,
                "sender": name,
            }
        return functools.partial(trader_node, name="Trader")