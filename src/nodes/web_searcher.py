from typing import Annotated, TypedDict

from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep

from nodes.base import create_react_agent_node


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    is_last_step: IsLastStep
    team_members: list[str]


system_prompt = """
あなたはウェブサーチャーエージェントです。
ツール`duckduckgo_results_json`を使用して最新情報を検索できる研究アシスタントです。
5回検索しても情報が得られない場合は、検索結果が得られないと報告してください。
URLからより詳細な情報が必要な場合はチームメンバーに連絡してください。
"""


def create_web_searcher_agent_node(name="WebSearcher"):
    return create_react_agent_node(
        name=name,
        tools=[DuckDuckGoSearchResults()],
        system_prompt=system_prompt,
        state_schema=State,
    )
