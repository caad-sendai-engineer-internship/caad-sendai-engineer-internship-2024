import json

from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda

from nodes.base import Node, llm

pre_system_prompt = """
あなたは、次の従業員間の会話をユーザーに返す最終回答を生成する任務を負った最終回答者です。: {members}
"""

post_system_prompt = """
上記の会話を踏まえて、最後のユーザーの質問に対して、ツール`final_answer`を使って最終回答を送信してください。
ツール`final_answer`の使用は一度だけのため、まとめて回答してください。
ユーザーに送りたいファイルがある場合は、`description`にはファイルのありかを記載しないでください、これはユーザーに伝わる際にダウンロードリンクに変換されるためです。
ユーザーに送りたいファイルがある場合は、`attachment_files`には次のファイルから選択してください。:\n{working_directory_files_message}
"""


def create_final_answerer_node(members: list[str], name: str = "FinalAnswerer") -> Node:
    function_def = {
        "type": "function",
        "function": {
            "name": "final_answer",
            "description": "最終回答を生成します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_answer": {
                        "description": "最終回答。ファイルの保存先や、ファイルのURLは含めないでください。",
                        "type": "string",
                    },
                    "attachment_files": {
                        "description": "添付ファイル。選択可能なファイルのパス。複数選択可能。",
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["final_answer", "attachment_files"],
            },
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", pre_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", post_system_prompt),
        ]
    ).partial(members=", ".join(members))

    chain = (
        prompt
        | llm.bind_tools(tools=[function_def])
        | JsonOutputKeyToolsParser(key_name="final_answer", first_tool_only=True)
        | {
            "messages": RunnableLambda(
                lambda x: [
                    HumanMessage(
                        content=json.dumps(x, indent=2, ensure_ascii=False), name=name
                    )
                ]
            ),
            "next": RunnableLambda(lambda _: None),
        }
    )

    return Node(name=name, runnable=chain)
