import os
from typing import Literal

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()


# Create prompt template
prompt = ChatPromptTemplate.from_messages(
    [("system", "{dialect}で返答してください。"), ("user", "{message}")]
)

# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)

# Create parser
parser = StrOutputParser()

# Create chain
chain = prompt | llm | parser
# response = chain.invoke({"dialect": "青森弁", "message": "こんにちは"})
# print(response)


# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    dialect: Literal["青森弁", "仙台弁", "大阪弁"]
    message: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = chain.invoke(user.model_dump())
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
