import time
import json
import nltk




#partition into days? i gues
def create_rewrite_node(llm): 
    def create_rewrite(state) -> dict:
        
        trader_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        
        prompt = f"""
        You are an expert in rewriting trading and investment plans that lack sufficient confidence. 
        Your task is to **evaluate and rewrite the trader’s investment plan** with rigor, clarity, and actionability.

        Contextual Inputs (use these to extract key metrics and insights):
        - **Market Research Report**: {market_research_report}
        - **Sentiment Report**: {sentiment_report}
        - **News Report**: {news_report}
        - **Fundamentals Report**: {fundamentals_report}

        Guidelines for Evaluation:
        1. **Extract Metrics from Context**: Identify and summarize quantitative/qualitative metrics 
        from the reports and the trader’s plan (ROI, risk-adjusted return, volatility, drawdowns, 
        liquidity, macro indicators, sentiment signals, news-driven catalysts).
        2. **Assess Argument Strength**: Check whether metrics are applied rigorously, consistently, and relevantly.
        3. **Evaluate Analytical Balance**: Identify overreliance on a single metric, missing counterarguments, 
        or lack of sensitivity analysis.
        4. **Scenario Testing**: Briefly stress-test the plan against at least one alternative scenario 
        (e.g., sudden volatility, interest rate shift, unexpected news).
        5. **Risk-Return Balance**: Explicitly discuss both upside potential and downside risks.
        6. **Refine the Trader's Plan**: Rewrite the plan based on strengths/weaknesses, 
        keeping recommendations concrete and actionable.
        7. **Comparative Transparency**: Clearly state how the revised plan improves on the original.

        Deliverables (use this structure in your answer):
        - **Summary of Current Situation**: Extracted key metrics and insights from the reports above.
        - **Summary of Original Plan**: Key points in {trader_plan}.
        - **Strengths & Weaknesses**: Highlight critical evaluation of the original plan.
        - **Rewritten Investment Plan**: Improved version, tailored for a professional trading audience.
        - **Final Recommendation**: Buy, Sell, or Hold (mandatory).
        - **Confidence Score**: Percentage (0-100%) of certainty in recommendation.
        - **Primary Risk Classification**: Choose one (Market Risk, Execution Risk, News/Headline Risk, Liquidity Risk).
        - **Scenario Sensitivity**: One "if-then" stress-test reflection.

        Tone: Professional, concise, and investment-focused.
        Ensure recommendations are **clear, evidence-based, and directly actionable**.
        """


        response = llm.invoke(prompt)
        
        return {
            "rewrite_plan": response.content
        }

    return create_rewrite
