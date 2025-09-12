import time
import json



def create_quality_manager(llm):
    def quality_manager_node(state) -> dict:
        trader_plan = state["investment_plan"]

        prompt = f"""
        You are acting as the **Quality Management Judge**. 
        Your role is to evaluate whether the trader's investment report is feasible and written with enough rigor 
        that an investor could feel confident in using it.

        Evaluation Criteria:
        1. **Key Metrics**: Are relevant quantitative and qualitative metrics (ROI, volatility, drawdowns, risk-adjusted returns, liquidity, market trends) clearly stated and appropriate?  
        2. **Argument Strength**: Are conclusions supported with consistent, rigorous, and relevant analysis?  
        3. **Analytical Balance**: Does the report avoid overreliance on a single factor, and consider counterarguments or sensitivity scenarios?  
        4. **Plan Feasibility**: Based on the above, is the trader’s plan practical and trustworthy for real-world decision making?  

        Trader’s Original Plan:
        {trader_plan}

        Deliverable:
        - Output a single float number between **0 and 1**, representing the confidence score in the feasibility of the plan.  
        - **No explanations, no extra text, just the number.**
        """

        response = llm.invoke(prompt)
      
        return {
            "confidence": response.content
        }

    return quality_manager_node
