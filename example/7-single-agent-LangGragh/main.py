import os
from typing import Type

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel as PydanticV1BaseModela
from langchain.pydantic_v1 import Field
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool, ToolException
from langchain_experimental.utilities import PythonREPL
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

load_dotenv()


# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)


# Create tool
class PythonExecutionInput(PydanticV1BaseModela):
    code: str = Field(description="実行するPythonコード。")
    is_secure: bool = Field(
        description="セキュリティを確保するために、このコードが安全であることを確認します。"
    )


class PythonExecutionTool(BaseTool):
    name: str = "python_execution"
    description: str = "これを使用して Python コードを実行します。値の出力を確認したい場合は、`print(...)` で出力する必要があります。これはユーザーに表示されます。"
    args_schema: Type[PydanticV1BaseModela] = PythonExecutionInput
    handle_tool_error: bool = True
    handle_validation_error: bool = True

    def _run(
        self,
        code: str,
        is_secure: bool,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        try:
            if not is_secure:
                raise ToolException("セキュアでないコードは実行できません。")
            if "plt.show(" in code:
                raise ToolException(
                    "plt.show() は実行できません。ファイルで出力してください。"
                )
            repl = PythonREPL()
            result = repl.run(code)
        except Exception as e:
            raise ToolException(f"Failed to execute. Error: {repr(e)}")
        return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"


python_execution_tool = PythonExecutionTool()

# Create graph
memory = MemorySaver()
graph = create_react_agent(
    llm,
    tools=[python_execution_tool],
    checkpointer=memory,
)

# Draw graph
graph.get_graph().draw_mermaid_png(
    output_file_path=f"{os.path.dirname(__file__)}/graph.png"
)


# Create chain
chain = graph | RunnableLambda(
    lambda x: (
        x["agent"]["messages"][-1].content
        if x.get("agent")
        else x["messages"][-1].content
    )
)
# response = chain.invoke(
#     {"messages": [HumanMessage(content="1 + 1は？")]},
#     config={"configurable": {"thread_id": "1"}}
# )
# print(response)


# App definition
app = FastAPI()


# Create request model
class UserRequest(BaseModel):
    message: str
    thread_id: str


# Adding route
@app.post("/conversation", tags=["conversation"])
async def conversation(user: UserRequest):
    response = chain.invoke(
        {"messages": [HumanMessage(content=user.message)]},
        config={"configurable": {"thread_id": user.thread_id}},
    )
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
