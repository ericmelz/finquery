from db_agent import DBAgent


class Orchestrator:
    """
    Class that manages flow between agents such as
    * DBAgent
    * PlotlyAgent
    * PresentationAgent

    Main class used by clients to ask and answer questions.
    """

    def __init__(self, db_url, model):
        self.sql_agent = DBAgent(db_url, model)

    def ask(self, question):
        pass
