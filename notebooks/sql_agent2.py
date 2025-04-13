from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from langsmith import Client
from typing_extensions import Annotated, TypedDict
from IPython.display import Markdown, display
import pandas as pd

import os

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntatically valid SQL query."]

def initialize_db_connection(db_user, db_pass, db_host, db_port, db_name):
    """Initialize SQLAlchemy engine and session for MySQL database."""
    try: 
        engine = create_engine(
            f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
            # echo=True, # Verbose logging for debugging
            echo=False, # Verbose logging for debugging
            pool_pre_ping=True # Ensure active connections
        )
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Database connection established!")
        return engine, session
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None, None

def get_sql_database(engine):
    """Wrap SQLAlchemy engine in LangChain's SQLDatabase."""
    try:
        db = SQLDatabase(engine)
        print("LangChain SQLDatabase initialized!")
        return db
    except Exception as e:
        print(f"Failed to initialize SQLDatabase: {e}")
        return None
    

class DBAgent:
    def __init__(self):
        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        model   = os.getenv('OPENAI_LLM_MODEL')
        self.engine, self.session = initialize_db_connection(db_user, db_pass, db_host, db_port, db_name)
        self.db = get_sql_database(self.engine)
        self.llm = init_chat_model(model, model_provider="openai")
        self.query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

    def generate_sql(self, question: str):
        """Generate a SQL query from a natural language question."""
        prompt = self.query_prompt_template.invoke(
            {
                "dialect": self.db.dialect,
                "top_k": 10,
                "table_info": self.db.get_table_info(),
                "input": question,
            }
        )
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return result["query"]

    def exec_and_render(self, sql):
        """Execute sql and return response as a dataframe and the dataframe's markdown"""
        with self.engine.connect() as connection:
            df = pd.read_sql(sql=text(sql), con=connection)
            if df.empty:
                return None, '**No Results**'
            else:
              return df, df.head().to_markdown()