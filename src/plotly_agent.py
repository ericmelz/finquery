from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from typing_extensions import Annotated, TypedDict

from db_agent import DBAgent


class PythonOutput(TypedDict):
    """Generated Python Ccode."""
    code: Annotated[str, ..., "Syntactically valid Python code."]


class PlotlyAgent:
    def __init__(self, db_agent: DBAgent, model):
        self.plotly_prompt_template = PromptTemplate.from_template("""
The user asked: "{question}"

Here is a preview of the query result:
{markdown_table}

Write Python code using Plotly to visualize this data. Do not include explanations—just a single Python code block.
DO NOT show the figure in the code.  For example be sure NOT to generate fig.show() in the code.  Instead, 
assign the figure to a variable named fig.

""")
        self.db_agent = db_agent
        self.llm = init_chat_model(model, model_provider="openai")

    def generate_plotly_code(self, question):
        """Given a natural language question, return sql and plotly code"""
        sql = self.db_agent.generate_sql(question)
        markdown_table = self.db_agent.exec_and_render(sql)
        plotly_prompt = self.plotly_prompt_template.format(
            question=question,
            markdown_table=markdown_table
        )
        structured_llm = self.llm.with_structured_output(PythonOutput)
        result = structured_llm.invoke(plotly_prompt)
        return sql, result["code"]
