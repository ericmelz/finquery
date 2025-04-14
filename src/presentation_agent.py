from langchain_openai import ChatOpenAI


def initialize_presentation_llm(model):
    """Set up OpenAI LLM for formatting outputs."""
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=0.2  # Slightly creative for natural summaries
        )
        return llm
    except Exception as e:
        print(f"Failed to initialize Presentation LLM: {e}")
        return None


class PresentationAgent:
    """Class for handling output of sql and plotly agents for clients"""

    def __init__(self, model):
        self.llm = initialize_presentation_llm(model)
        if not self.llm:
            raise Exception("Error initializing presentation agent.")

    def format_output(self, question, db_result=None, plotly_result=None):
        try:
            prompt = f"""
            Given the natural language question: '{question}'
            {', and the sql result: ' + db_result + ' ' if db_result else ''}
            {', and the plotly visualization code: ' + plotly_result + ' ' if plotly_result else ''}
            Generate a concise, readable summary for a non-technical user. Include natural language explanations
            and, if visualization code is provided, a brief description of what it shows.        
            """
            response = self.llm.invoke(prompt).content
            return f"Summary for '{question}:\n{response}"
        except Exception as e:
            return f"Error formatting output for '{question}': {e}"
