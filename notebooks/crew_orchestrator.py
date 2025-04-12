from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from sql_agent import create_sql_agent, run_query
from python_agent import create_plotviz_executor, run_visualization
from presentation_agent import format_output


# ---- Routing Option 1: Rule-Based Router ----
def rule_based_router(query):
    """Route queries using simple keyword rules with standalone Presentation Agent."""
    sql_agent = create_sql_agent()
    viz_agent = create_plotviz_executor()

    if "plot" in query.lower() or "chart" in query.lower():
        sql_result = run_query(sql_agent, query)
        viz_result = run_visualization(viz_agent, query)
        return format_output(query, sql_result, viz_result)
    else:
        sql_result = run_query(sql_agent_instance, query)
        return format_output(query, sql_result)


