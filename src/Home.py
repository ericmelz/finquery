import streamlit as st
from sqlalchemy import create_engine, text

if "db_engine" not in st.session_state:
    st.session_state.db_engine = None
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

    if st.button("Save and Connect"):
        try:
            # Create a connection and test it
            db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(db_url, pool_pre_ping=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            st.session_state.db_engine = engine
            st.session_state.connection_status = "Connected successfully!"
        except Exception as e:
            st.session_state.connection_status = f"Connection failed: {e}"


# Main window
st.title("Finquery")
st.markdown("This agent can help you with SQL queries and Python code for data analysis. Configure your MySQL database "
            "connection using the sidebar.")

if "success" in st.session_state.connection_status:
    st.info(st.session_state.connection_status)
else:
    st.warning(st.session_state.connection_status)


