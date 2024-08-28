from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from nodes.base import Node, llm

pre_system_prompt = """
あなたは、次の従業員間の会話を管理する任務を負ったスーパーバイザーです。: {members}
次のユーザー要求が与えられた場合、ワーカーが次に行動するように応答します。
各ワーカーはタスクを実行し、結果とステータスを返します。
ユーザーの要求が明確でない場合や、回答が出せる状態になったら、{final} で応答します。
"""

post_system_prompt = """
上記の会話を踏まえて、次に誰が行動すべきでしょうか?
それとも終わらせるべきでしょうか？
次のいずれかを選択します: {members}
ツール`route`を使って次に行動するメンバーを選択してください。
ツール`route`の使用は一度だけです。
同じメンバーを連続して選択することはできません。
"""


def create_team_supervisor_node(
    members: list[str], final: str, name: str = "Supervisor"
) -> Node:
    _members = members + [final]
    function_def = {
        "type": "function",
        "function": {
            "name": "route",
            "description": "次の役割を選択します。",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": _members},
                        ],
                    },
                },
                "required": ["next"],
            },
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", pre_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", post_system_prompt),
        ]
    ).partial(members=", ".join(_members), final=final)

    cahin = (
        prompt
        | llm.bind_tools(tools=[function_def])
        | JsonOutputKeyToolsParser(key_name="route", first_tool_only=True)
    )

    return Node(name=name, runnable=cahin)
