from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType, create_openai_functions_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain import hub
import pandas as pd
from constants import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME, OPENAI_API_KEY, OPENAI_LLM_MODEL

# Step 1: Set up database connection with SQLAlchemy
def initialize_db_connection():
    """Initialize SQLAlchemy engine and session for MySQL database."""
    try:
        engine = create_engine(
            f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            echo=True, # Verbose logging for debugging
            pool_pre_ping=True # Ensure active connections
        )
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Database connection established!")
        return engine, session
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None, None

# Step 2: Configure LangChain SQLDatabase
def get_sql_database(engine):
    """Wrap SQLAlchemy engine in LangChain's SQLDatabase."""
    try:
        db = SQLDatabase(engine)
        print("LangChain SQLDatabase initialized!")
        return db
    except Exception as e:
        print(f"Failed to initialize SQLDatabase: {e}")
    return None

# Step 3: Initialize LLM
def initialize_llm():
    """Set up OpenAI LLM with API key"""
    try:
        llm = ChatOpenAI(
            model=OPENAI_LLM_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0
        )
        print("OpenAI LLM initialized!")
        return llm
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
    return None

# Step 4: Get DB Toolkit
def get_db_toolkit(db, llm):
    """Get SQLDatabaseToolkit"""
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        print("DB Toolkit initialized!")
        return toolkit
    except Exception as e:
        print(f"failed to get db tool: {e}")
    return None

# Step 5: Create PythonREPLTool
def get_repl_tool():
    """Instantiate a PythonREPLTool"""
    try:
        repl = PythonREPLTool()
        print("REPL Tool initialized!")
        return repl
    except Exception as e:
        print(f"Failed to get REPL Tool: {e}")
    return None

# Step 6: Generate SQL+Viz Prompt
# def get_prompt():
#     """Set up a prompt instructing the agent to generate SQL then Plotly code."""
#     try:
#         # instructions = """You are an agent designed to query a MySQL database and generate Python code for plotting data using Plotly.
#         # Input will be a natural language query (e.g., 'Plot monthly sales as a line chart').
#         # 1. Generate a SQL query to fetch the required data from the database.
#         # 2. Use the SQL results to create Plotly code (not Matplotlib) and return it in ```python <code>``` format.
#         # If the query is unclear or data is unavailable, return 'Insufficient data for visualization'.
#         # Assume the database has tables like 'orders' (for SalesTrend) or 'transactions' (for FinQuery)."""
#         instructions = '''Generate SQL queries from natural language requests, fetch data, and create Plotly visualizations.'''
#         prompt = hub.pull("langchain-ai/openai-functions-template").partial(instructions=instructions)
#         print("Prompt initialized!")
#         return prompt
#     except Exception as e:
#         print(f"Failed to generate prompt: {e}")
#         return None


# Step 6: Create SQL Agent
def create_db_agent(db_toolkit, llm):
    """Build SQL agent with LangChain toolkit."""
    try:
        agent = create_sql_agent(
            llm=llm,
            toolkit=db_toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, # React-based reasoning
            verbose=True, # Show intermediate steps
        )
        print("SQL Agent created successfully!")
        return agent
    except Exception as e:
        print(f"Failed to create agent: {e}")
    return None    


# Step 7: Create Plotly prompt
def create_plotly_prompt():
    try:
        instructions = '''Generate SQL queries from natural language requests, fetch data, and create Plotly visualizations.'''
        prompt = hub.pull('langchain-ai/openai-functions-template').partial(instructions=instructions)
        if prompt:
            print("Plotly Prompt created successfully!")
            return prompt
    except Exception as e:
        print(f"Failed to create plotly prompt: {e}")
    return None


# Step 8: Create Plotly Agent
def create_plotly_agent(repl_tool, llm, prompt):
    """Build SQL+Viz agent with LangChain toolkit."""
    tools = [repl_tool]
    try:
        agent = create_openai_functions_agent(llm, tools, prompt)
        print("Plotly Agent initialized!")
        return agent
    except Exception as e:
        print(f"Failed to create agent: {e}")
    return None

# Step 9: Create plotly agent executor
def create_plotly_executor(agent, tools):    
    try:
        executor = AgentExecutor(agent=agent, tools=tools)
        print("Plotly Executor initialized!")
        return executor
    except Exception as e:
        print(f"Failed to create executor: {e}")
    return None

# Step 10: Build plotviz executor (main function)
def create_plotviz_executor():
    """Build an agent executor for SQL+Viz capabilities"""
    try:
        engine, session = initialize_db_connection()
        if engine and session:
            db = get_sql_database(engine)
            if db:
                llm = initialize_llm()
                if llm:
                    db_toolkit = get_db_toolkit(db, llm)
                    if db_toolkit:
                        sql_agent = create_db_agent(db_toolkit, llm)
                        if sql_agent:
                            repl_tool = get_repl_tool()
                            if repl_tool:
                                plotly_prompt = create_plotly_prompt()
                                if plotly_prompt:
                                    plotly_agent = create_plotly_agent(repl_tool, llm, plotly_prompt)
                                    if plotly_agent:
                                        plotly_executor = create_plotly_executor(plotly_agent, [repl_tool])
                                        if plotly_executor:
                                            def plotviz_executor(query):
                                                sql_query = query + ".\nGenerate only the SQL code to create this chart.  Do not produce a natural language response."
                                                print(f"*** sql_query:\n {sql_query}")
                                                sql_response = sql_agent.run(sql_query)
                                                print(f"*** Sql Response: {sql_response}")
                                                if '```sql' not in sql_response:
                                                    print("*** ERROR: was expecting ```sql in Sql Response but it's not there!!!")
                                                sql_code = sql_response.split('```sql')[1].split('```')[0].strip()
                                                print(f"*** Sql code:\n{sql_code}\n***")
                                                with engine.connect() as connection:
                                                    df = pd.read_sql(sql=text(sql_code), con=connection)
                                                if df.empty:
                                                    return 'Insufficient data for visualization.'
                                                plotly_query = f'{query}.  Data: {df.head().to_markdown()} Generate Plotly code.'
                                                print(f"*** Plotly Query:\n{plotly_query}\n***")
                                                plotly_response = plotly_executor.invoke({'input': plotly_query})['output']
                                                print(f"*** Plotly Response: {plotly_response}")
                                                plotly_code = plotly_response.split('```python')[1].split('```')[0].strip()
                                                return plotly_code
                                            return plotviz_executor
    except Exception as e:
        print(f"Failed to create plotviz executor: {e}")
    return None


def run_visualization(plotviz_executor, query):
    return plotviz_executor(query)
    