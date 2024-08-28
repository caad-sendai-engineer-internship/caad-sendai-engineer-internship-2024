import os
from functools import partial
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from nodes.base import Node
from nodes.team_supervisor import create_team_supervisor_node
from nodes.web_scraper import create_web_scraper_agent_node
from nodes.web_searcher import create_web_searcher_agent_node


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    team_members: str
    next: str | None


def create_web_research_workflow() -> Runnable:
    web_scraper_agent_node = create_web_scraper_agent_node()
    web_searcher_agent_node = create_web_searcher_agent_node()

    operation_members: list[Node] = [
        web_scraper_agent_node,
        web_searcher_agent_node,
    ]

    team_supervisor_node = create_team_supervisor_node(
        members=[member.name for member in operation_members],
        final="FINISH",
    )

    nodes = [
        *operation_members,
        team_supervisor_node,
    ]

    graph_builder = StateGraph(State)

    for node in nodes:
        graph_builder.add_node(node=node.name, action=node.runnable)

    for node in operation_members:
        graph_builder.add_edge(
            start_key=node.name,
            end_key=team_supervisor_node.name,
        )

    graph_builder.add_conditional_edges(
        source=team_supervisor_node.name,
        path=lambda x: x["next"],
        path_map={
            web_scraper_agent_node.name: web_scraper_agent_node.name,
            web_searcher_agent_node.name: web_searcher_agent_node.name,
            "FINISH": END,
        },
    )

    graph_builder.set_entry_point(key=team_supervisor_node.name)

    graph = graph_builder.compile()

    graph.get_graph().draw_mermaid_png(
        output_file_path=f"{os.path.dirname(__file__)}/{__name__}.png"
    )

    return (
        partial(
            web_research_graph_enter_chain,
            members=[node.name for node in operation_members],
        )
        | graph
    )


def web_research_graph_enter_chain(
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
