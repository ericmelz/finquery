from typing import TypedDict, Annotated

import pandas as pd
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def initialize_db_connection(db_url):
    """Initialize SQLAlchemy engine and session for MySQL database."""
    try:
        engine = create_engine(
            db_url,
            # echo=True, # Verbose logging for debugging
            echo=False,  # Verbose logging for debugging
            pool_pre_ping=True  # Ensure active connections
        )
        session = sessionmaker(bind=engine)()
        return engine, session
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None, None


def get_sql_database(engine):
    """Wrap SQLAlchemy engine in LangChain's SQLDatabase."""
    try:
        db = SQLDatabase(engine)
        return db
    except Exception as e:
        print(f"Failed to initialize SQLDatabase: {e}")
        return None


class QueryOutput(TypedDict):
    """Model for generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


class DBAgent:
    """Agent for generating and executing SQL"""
    def __init__(self, db_url, model):
        self.engine, self.session = initialize_db_connection(db_url)
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
