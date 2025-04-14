from db_agent import DBAgent


class Orchestrator:
    """
    Class that manages flow between agents such as
    * DBAgent
    * PlotlyAgent
    * PresentationAgent

    Main class used by clients to ask and answer questions.
    """

    def __int__(self, db_host, db_port, db_user, db_pass, db_name, model):
        self.sql_agent = DBAgent(db_host, db_port, db_user, db_pass, db_name, model)

    def ask(self, question):
        pass
