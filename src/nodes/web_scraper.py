from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep

from nodes.base import create_react_agent_node
from tools.scrape_webpages import ScrapeWebpagesTool


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    is_last_step: IsLastStep
    team_members: list[str]


system_prompt = """
あなたはウェブスクレイパーエージェントです。
ツール`scrape_webpages`関数を使用して、指定された URL からより詳細な情報を取得できる研究アシスタントです。
URLの形式が正しくない場合は、URLが正しくないと報告してください。
検索クエリでより詳細な情報が必要な場合はチームメンバーに連絡してください。
"""


def create_web_scraper_agent_node(name="WebScraper"):
    return create_react_agent_node(
        name=name,
        tools=[ScrapeWebpagesTool()],
        system_prompt=system_prompt,
        state_schema=State,
    )
