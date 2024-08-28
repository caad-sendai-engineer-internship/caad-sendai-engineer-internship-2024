import os
from enum import StrEnum
from typing import Annotated, TypedDict

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

load_dotenv()


class Dialect(StrEnum):
    AOMORI = "青森弁"
    SENDAI = "仙台弁"
    OSAKA = "大阪弁"


# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)


# Create graph
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    dialect: Dialect


def chatbot(state: State):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{dialect}で返答してください。",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = prompt | llm
    return {"messages": [chain.invoke(state)]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Draw graph
graph.get_graph().draw_mermaid_png(
    output_file_path=f"{os.path.dirname(__file__)}/graph.png"
)


# Create chain
chain = graph | RunnableLambda(
    lambda x: (
        x["chatbot"]["messages"][-1].content
        if x.get("chatbot")
        else x["messages"][-1].content
    )
)
# response = chain.invoke(
#     {"messages": [HumanMessage(content="こんにちは、わたしはトムです")], "dialect": Dialect.AOMORI},
#     config={"configurable": {"thread_id": "1"}}
# )
# print(response)


# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    dialect: Dialect
    message: str
    thread_id: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = chain.invoke(
        {"messages": [HumanMessage(content=user.message)], "dialect": user.dialect},
        config={"configurable": {"thread_id": user.thread_id}},
    )
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
