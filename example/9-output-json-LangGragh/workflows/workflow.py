import os
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langchain_core.runnables import Runnable, chain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from nodes.data_scientist import create_data_scientist_agent_node
from nodes.final_answerer import create_final_answerer_node


class UserInput(TypedDict):
    messages: list[AnyMessage]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next: str
    working_directory: str | None
    working_directory_files: list[str] | None
    working_directory_files_message: str | None


def create_workflow() -> Runnable:
    data_scientist_agent_node = create_data_scientist_agent_node()
    final_answerer_node = create_final_answerer_node(
        members=[data_scientist_agent_node.name]
    )

    nodes = [
        data_scientist_agent_node,
        final_answerer_node,
    ]

    graph_builder = StateGraph(State)

    for node in nodes:
        graph_builder.add_node(node=node.name, action=node.runnable)

    graph_builder.set_entry_point(key=data_scientist_agent_node.name)

    graph_builder.add_edge(
        start_key=data_scientist_agent_node.name,
        end_key=final_answerer_node.name,
    )

    graph_builder.set_finish_point(key=final_answerer_node.name)

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    graph.get_graph().draw_mermaid_png(
        output_file_path=f"{os.path.dirname(__file__)}/{__name__}.png"
    )

    return graph | graph_output_parser


@chain
def graph_output_parser(response: dict) -> str:
    if isinstance(response, list):
        response = response[-1]

    if response.get("FinalAnswerer"):
        response = response["FinalAnswerer"]

    return response["messages"][-1].content
