from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from sql_agent2 import DBAgent
from plotly_agent import PlotlyAgent
from presentation_agent import format_output
from constants import OPENAI_API_KEY


# ---- Routing Option 1: Rule-Based Router ----
def rule_based_router(question):
    """Route queries using simple keyword rules with standalone Presentation Agent."""
    sql_agent = DBAgent()
    viz_agent = PlotlyAgent(sql_agent)

    if "plot" in question.lower() or "chart" in question.lower():
        sql_query, python_code = viz_agent.generate_plotly_code(question)
        df, markdown = sql_agent.exec_and_render(sql_query)
        return format_output(question, sql_result=markdown, viz_result=python_code)
    else:
        sql_query = sql_agent.generate_sql(question)
        df, markdown = sql_agent.exec_and_render(sql_query)
        return format_output(question, sql_result=markdown, viz_result=None)


# --- Routing Option 2: AI-Powered Router ---
def classify_intent(query):
    """Classify the intended presentation style of the query."""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
    prompt = f"""
    Classify "Query" as 'SQL', 'Visualization', or 'Both'.  
    Response with ONLY 'SQL', 'Visualization', or 'Both'.
    DO NOT return any explanation as to why you chose one of those values.
    Query: {query}'
    """
    intent = llm.invoke(prompt).content.lower()
    return intent

def ai_powered_router(question):
    """Use LLM to classify query intent and route with standalone Presntation Agent."""
    sql_agent = DBAgent()
    viz_agent = PlotlyAgent(sql_agent)

    prompt = f"Classify this query as 'SQL', 'Visualization', or 'Both': {question}'"
    intent = classify_intent(question)

    print(f'*** presentation intent={intent}')
    if intent == 'sql':
        sql_query = sql_agent.generate_sql(question)
        df, markdown = sql_agent.exec_and_render(sql_query)
        return format_output(question, sql_result=markdown, viz_result=None)
    elif intent == 'visualization':
        sql_query, python_code = viz_agent.generate_plotly_code(question)
        return format_output(question, sql_result=None, viz_result=python_code)
    elif intent == 'both':
        sql_query, python_code = viz_agent.generate_plotly_code(question)
        df, markdown = sql_agent.exec_and_render(sql_query)
        return format_output(question, sql_result=markdown, viz_result=python_code)
    else:
        raise Exception(f"Unknown intent: {intent}")