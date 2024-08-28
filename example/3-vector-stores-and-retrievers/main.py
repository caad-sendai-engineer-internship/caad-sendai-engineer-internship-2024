import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import BaseModel

load_dotenv()

INPUT_MD_FILE = f"{os.path.dirname(__file__)}/import.md"
OUTPUT_CHROMA_FILE = f"{os.path.dirname(__file__)}/chroma_db"


# Create embedding
embedding = AzureOpenAIEmbeddings(
    azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME"],
)

# Create vectorstore
if not os.path.exists(OUTPUT_CHROMA_FILE):
    print("Creating new Chroma vectorstore")
    loader = UnstructuredMarkdownLoader(INPUT_MD_FILE, mode="elements", strategy="fast")
    documents = loader.load()
    documents = filter_complex_metadata(documents)
    vectorstore = Chroma.from_documents(
        documents, embedding=embedding, persist_directory=OUTPUT_CHROMA_FILE
    )
else:
    print("Loading existing Chroma vectorstore")
    vectorstore = Chroma(
        persist_directory=OUTPUT_CHROMA_FILE, embedding_function=embedding
    )


# Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},
)


# Create prompt template
message = """
あなたは質問応答タスクのアシスタントです。次の取得したコンテキストを使用して質問に答えてください。答えがわからない場合は、わからないと言ってください。最大で3文を使用し、答えを簡潔にしてください。
質問: {message}
コンテキスト: {context}
答え:
"""
prompt = ChatPromptTemplate.from_messages([("human", message)])

# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)

# Create parser
parser = StrOutputParser()

# Create chain
rag_chain = (
    {"context": retriever, "message": RunnablePassthrough()} | prompt | llm | parser
)
# response = rag_chain.invoke("icaseとはなんですか？")
# print(response)


# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    message: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = rag_chain.invoke(user.message)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
