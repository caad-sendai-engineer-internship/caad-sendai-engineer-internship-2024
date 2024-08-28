import os
from operator import itemgetter
from typing import Literal

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, trim_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# Create prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "あなたはアシスタントです。すべての質問に{language}で答えてください。",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    model="gpt-4o",
    temperature=0,
)

# Create parser
parser = StrOutputParser()

# Create trimmer
trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Create chain
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer)
    | prompt
    | llm
    | parser
)

# Create runnable with message history
with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)
# config = {"configurable": {"session_id": "1"}}
# response = with_message_history.invoke(
#     {
#         "messages": [HumanMessage(content="こんにちは")],
#         "language": "英語",
#     },
#     config={"configurable": {"session_id": "1"}},
# )
# print(response)


# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    language: Literal["英語", "日本語"]
    message: str
    session_id: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content=user.message)],
            "language": user.language,
        },
        config={"configurable": {"session_id": user.session_id}},
    )
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
