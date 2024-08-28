import os
from functools import partial
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langchain_core.runnables import Runnable, chain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from constants import WORKING_DIRECTORY
from nodes.base import Node
from nodes.data_scientist import create_data_scientist_agent_node
from nodes.final_answerer import create_final_answerer_node
from nodes.team_supervisor import create_team_supervisor_node
from nodes.working_directory_checker import create_working_directory_checker_node
from workflows.web_research import create_web_research_workflow


class UserInput(TypedDict):
    messages: list[AnyMessage]


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next: str | None
    team_members: str
    working_directory: str | None
    working_directory_files: list[str] | None
    working_directory_files_message: str | None


@chain
def join_graph(response: dict) -> dict:
    return {"messages": [response["messages"][-1]]}


def create_super_workflow() -> Runnable:
    working_directory_checker_node = create_working_directory_checker_node(
        working_directory=WORKING_DIRECTORY
    )
    data_scientist_agent_node = create_data_scientist_agent_node()
    web_research_graph_node = Node(
        name="WebResearchTeam", runnable=(create_web_research_workflow() | join_graph)
    )

    operation_members: list[Node] = [
        data_scientist_agent_node,
        web_research_graph_node,
    ]

    final_answerer_node = create_final_answerer_node(
        members=[member.name for member in operation_members]
    )

    team_supervisor_node = create_team_supervisor_node(
        members=[member.name for member in operation_members],
        final=final_answerer_node.name,
    )

    nodes = [
        *operation_members,
        final_answerer_node,
        team_supervisor_node,
        working_directory_checker_node,
    ]

    graph_builder = StateGraph(State)

    for node in nodes:
        graph_builder.add_node(node=node.name, action=node.runnable)

    for node in operation_members:
        graph_builder.add_edge(start_key=node.name, end_key=team_supervisor_node.name)

    graph_builder.add_conditional_edges(
        source=team_supervisor_node.name,
        path=lambda x: x["next"],
        path_map={
            data_scientist_agent_node.name: data_scientist_agent_node.name,
            web_research_graph_node.name: web_research_graph_node.name,
            final_answerer_node.name: working_directory_checker_node.name,
        },
    )

    graph_builder.add_conditional_edges(
        source=working_directory_checker_node.name,
        path=lambda x: x["next"],
        path_map={
            None: team_supervisor_node.name,
            final_answerer_node.name: final_answerer_node.name,
        },
    )

    graph_builder.set_entry_point(key=working_directory_checker_node.name)
    graph_builder.set_finish_point(key=final_answerer_node.name)

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    graph.get_graph().draw_mermaid_png(
        output_file_path=f"{os.path.dirname(__file__)}/{__name__}.png"
    )

    return (
        partial(
            super_graph_enter_chain, members=[node.name for node in operation_members]
        )
        | graph
        | super_graph_output_parser
    )


@chain
def super_graph_output_parser(response: dict) -> str:
    if isinstance(response, list):
        response = response[-1]

    if response.get("FinalAnswerer"):
        response = response["FinalAnswerer"]

    return response["messages"][-1].content


def super_graph_enter_chain(
    state: dict,
    members: list[str],
) -> dict:
    results = {
        "messages": state["messages"],
        "team_members": ", ".join(
            [member for member in members if member not in [START, END]]
        ),
    }
    return results
