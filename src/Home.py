import os

import streamlit as st
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from orchestrator import Orchestrator

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Not connected.  Provide credentials and click the button in the sidebar."


# Sidebar: Database Configuration
with st.sidebar:
    st.header("DATABASE CONFIGURATION")
    st.markdown("Enter MySQL connection details:")

    db_user = st.text_input("User", value=st.secrets["DB_USER"])
    db_pass = st.text_input("Password", type="password", value=st.secrets["DB_PASS"], key="db_pass")
    db_host = st.text_input("Host", value=st.secrets["DB_HOST"], key="db_host")
    db_port = st.text_input("Port", value=st.secrets["DB_PORT"], key="db_port")
    db_name = st.text_input("Name", value=st.secrets["DB_NAME"], key="db_name")
    model = st.secrets["OPENAI_LLM_MODEL"]
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    if st.button("Connect"):
        try:
            # Create a connection and test it
            db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(db_url, pool_pre_ping=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            st.session_state.orchestrator = Orchestrator(db_url, model)
            st.session_state.connection_status = "Connected successfully!"
        except Exception as e:
            st.session_state.connection_status = f"Connection failed: {e}"

    if "success" in st.session_state.connection_status:
        st.info(st.session_state.connection_status)
    else:
        st.warning(st.session_state.connection_status)


# Main window
st.title("Finquery")
st.markdown("This agent can help you with SQL queries and Python code for data analysis. Configure your MySQL database "
            "connection using the sidebar.")

# Reset Chat button
if st.button("Reset Chat"):
    st.session_state.chat_history = []
    st.session_state.connection_status = "Not connected.  Provide credentials and click the button in the sidebar."
    st.session_state.db_engine = None
    st.rerun()

# Show message history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        elif message["role"] == "assistant":
            ai_response = message["ai_response"]
            if ai_response.python is not None:
                print(f'---Python---\n{ai_response.python}\n---')
                local_vars = {}
                exec(ai_response.python, {"px": px, "go": go, "pd": pd}, local_vars)
                for var_name, var_value in local_vars.items():
                    if isinstance(var_value, go.Figure):
                        st.plotly_chart(var_value)
                        break
            if ai_response.df is not None:
                st.dataframe(ai_response.df)
            st.markdown(ai_response.explanation)
        else:
            raise Exception(f"Unknown role: {message['role']}")


def ask(question):
    answer = st.session_state.orchestrator.ask(question)
    return answer


if prompt_question := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt_question)
    st.session_state.chat_history.append({"role": "user", "content": prompt_question})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = ask(prompt_question)
    st.session_state.chat_history.append({"role": "assistant", "ai_response": assistant_response})
    st.rerun()
