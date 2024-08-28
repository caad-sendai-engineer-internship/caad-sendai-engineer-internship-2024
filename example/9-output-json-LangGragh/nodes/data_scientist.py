from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep

from nodes.base import create_react_agent_node
from tools.python_repl import PythonReplTool


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    is_last_step: IsLastStep
    working_directory: str


system_prompt = """
あなたはデータサイエンティストです。
"""


def create_data_scientist_agent_node(name="DataScientist"):
    return create_react_agent_node(
        name=name,
        tools=[PythonReplTool()],
        system_prompt=system_prompt,
        state_schema=State,
    )
