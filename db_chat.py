from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.memory import ConversationBufferMemory
import time
from conf import *
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI


class ChatAgent:
    def __init__(self, llm_key, llm_model, temperature=0):
        self.username = db_username
        self.password = db_password
        self.host = db_host
        self.dbname = db_name
        self.db_uri = f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}/{self.dbname}"
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature, openai_api_key=llm_key)
        self.db = SQLDatabase.from_uri(self.db_uri)
        self.load_prompt()
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        '''self.memory = ConversationBufferMemory(
            input_key="input", output_key="output", memory_key="history", return_messages=True)'''
        #self.defineAgentMemory()
        '''self.agent = create_sql_agent(llm=self.llm,
                                      prompt=self.prompt, agent_type="openai-tools", toolkit=self.toolkit, verbose=True)'''

    def load_prompt(self):
        with open("prompt.txt", "r") as file:
            self.system = file.read()

        self.prompt = ChatPromptTemplate.from_messages(
            [("system", self.system), MessagesPlaceholder("history", optional=True), ("human", "{input}"), MessagesPlaceholder("agent_scratchpad")]
        )

    def defineAgentMemory(self):
        self.memory = ConversationBufferMemory(
            input_key="input", output_key="output", memory_key="history", return_messages=True)
        self.agent = create_sql_agent(llm=self.llm, agent_executor_kwargs={"memory": self.memory}, prompt=self.prompt,
                                      agent_type="openai-tools", toolkit=self.toolkit,verbose=True)
        return self.agent, self.memory


def ask_query(agent, question, memory):
    start = time.time()
    res = agent.invoke({"input": question, 'history': memory})
    end = time.time()
    print(f"Inference Time: {end - start}")
    return res


if __name__ == "__main__":
    main = ChatAgent(api_key, model)
    agent, memory = main.defineAgentMemory()
    ask = ''
    while True:
        ask = input("Ask a Question : ")
        if ask == '0':
            print("Thanks for your time")
            break
        response = ask_query(agent, ask, memory)
        print(response)