import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()


def web_loader(url: str):
    loader = WebBaseLoader(url)
    return loader.load()


# Create prompt template
message = """
次の内容について概要を日本語で答えてください：


"{text}"


概要:
"""
prompt = ChatPromptTemplate.from_messages([("human", message)])


# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)

# Create chain
chain = (
    RunnableLambda(web_loader)
    | load_summarize_chain(llm=llm, chain_type="stuff", prompt=prompt)
    | RunnableLambda(lambda x: x["output_text"])
)
# response = chain.invoke("https://rye.astral.sh/guide/basics/")

# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    message: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = chain.invoke(user.message)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
