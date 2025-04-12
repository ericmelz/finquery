from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from sql_agent import initialize_db_connection, get_sql_database, initialize_llm, create_agent as create_sql_agent, run_query
#from python_agent import initialize_python_agent, run_visualization
from presentation_agent import format_output

engine, session = initialize_db_connection()
db = get_sql_database(engine)
llm = initialize_llm()



