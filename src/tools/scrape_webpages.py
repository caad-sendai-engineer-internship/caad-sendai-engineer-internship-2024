from typing import Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import BaseTool


class ScrapeWebpagesInput(BaseModel):
    urls: list[str] = Field(
        description="スクレイピングする URL のリスト。Web ページのみが許可されます。PDF などのファイルを指す URL は許可されません。"
    )


class ScrapeWebpagesTool(BaseTool):
    name: str = "scrape_webpages"
    description: str = "提供された Web ページから詳細情報を取得するために、requests と bs4 を使用します。"
    args_schema: Type[BaseModel] = ScrapeWebpagesInput
    handle_tool_error: bool = True
    handle_validation_error: bool = True

    def _run(
        self, urls: list[str], run_manager: CallbackManagerForToolRun | None = None
    ) -> str:
        loader = WebBaseLoader(urls)
        docs = loader.load()
        return "\n\n".join(
            [
                f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
                for doc in docs
            ]
        )
