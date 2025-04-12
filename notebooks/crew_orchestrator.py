from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from sql_agent import create_sqldb_agent, run_query
from python_agent import create_plotviz_executor, run_visualization
from presentation_agent import format_output
from constants import OPENAI_API_KEY


# ---- Routing Option 1: Rule-Based Router ----
def rule_based_router(query):
    """Route queries using simple keyword rules with standalone Presentation Agent."""
    sql_agent = create_sqldb_agent()
    viz_agent = create_plotviz_executor()

    if "plot" in query.lower() or "chart" in query.lower():
        sql_result = run_query(sql_agent, query)
        viz_result = run_visualization(viz_agent, query)
        return format_output(query, sql_result, viz_result)
    else:
        sql_result = run_query(sql_agent, query)
        return format_output(query, sql_result)


# --- Routing Option 2: AI-Powered Router ---
def classify_intent(query):
    """Classify intent.  This returns a chatty response"""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
    prompt = f"Classify this query as 'SQL', 'Visualization', or 'Both': {query}'"
    intent = llm.invoke(prompt).content.lower()
    return intent

def classify_intent_no_fluff(query):
    """Classify intent.  This returns a concise response"""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
    prompt = f"""
    Classify "Query" as 'SQL', 'Visualization', or 'Both'.  
    Response with ONLY 'SQL', 'Visualization', or 'Both'.
    DO NOT return any explanation as to why you chose one of those values.
    Query: {query}'
    """
    intent = llm.invoke(prompt).content.lower()
    return intent

def ai_powered_router(query):
    """Use LLM to classify query intent and route with standalone Presntation Agent."""
    sql_agent = create_sqldb_agent()
    viz_agent = create_plotviz_executor()

    prompt = f"Classify this query as 'SQL', 'Visualization', or 'Both': {query}'"
    intent = classify_intent_no_fluff(query)

    intent = intent.lower()
    print(f'*** presentation intent={intent}')
    if intent == 'both':
        sql_result = run_query(sql_agent, query)
        viz_result = run_visualization(viz_agent, query)
        return format_output(query, sql_result, viz_result)
    elif intent == 'visualization':
        viz_result = run_visualization(viz_agent, query)
        return format_output(query, None, viz_result)
    elif intent == 'sql':
        sql_result = run_query(sql, agent)
        return format_output(query, sql_result)
    else:
        raise Exception(f"Unknown intent: {intent}")