from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType
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

# Step 3: Initialize OpenAI LLM
def initialize_llm():
    """Set up OpenAI LLM with API key"""
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini", # Cost-effective model: adjust as needed
            api_key=OPENAI_API_KEY,
            temperature=0
        )
        print("OpenAI LLM initialized!")
        return llm
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
        return None

# Step 4: Create SQL Agent
def create_agent(db, llm):
    """Build SQL agent with LangChain toolkit."""
    try:
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, # React-based reasoning
            verbose=True, # Show intermediate steps
        )
        print("SQL Agent created successfully!")
        return agent
    except Exception as e:
        print(f"Failed to create agent: {e}")
        return None

def create_sqldb_agent():
    """Build SQL agent"""
    engine, session = initialize_db_connection()
    db = get_sql_database(engine)
    llm = initialize_llm()
    return create_agent(db, llm)

# Step 5: Process Query and Format Output
def run_query(agent, query):
    """Execute a natural language query and return formatted response."""
    try:
        print(f"sql_agent.run_query: {query=}")
        response = agent.run(query)
        print(f"sql_agent.run_query: {response=}")        
        # Format raw SQL output into natural language
        if "No results found" in response:
            return f"Sorry, I couldn't find any data for : '{query}'."
        else:
            return f"Here's what I found for '{query}':\n{response}"
    except Exception as e:
        return f"Error processing query '{query}': {e}"
        