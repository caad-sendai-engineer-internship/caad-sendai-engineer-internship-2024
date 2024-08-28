import os
from dataclasses import dataclass
from typing import Type

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_openai import AzureChatOpenAI
from langgraph.graph import MessagesState, StateGraph

from nodes.custom_tool_node import CustomToolNode, tools_condition

StateSchemaType = Type[MessagesState]

llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    model=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)

llm_mini = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_MINI_DEPLOYMENT_NAME"],
    model=os.environ["AZURE_OPENAI_CHAT_MODEL_MINI_DEPLOYMENT_NAME"],
    temperature=0,
)


@dataclass
class Node:
    name: str
    runnable: Runnable


def create_react_agent_node(
    name: str,
    llm: AzureChatOpenAI = llm,
    tools: list = [],
    system_prompt: str = "",
    state_schema: StateSchemaType | None = None,
) -> Node:
    system_prompt += (
        "\n利用可能なツールを使って、自分の専門分野に応じて自律的に作業してください。"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    model_runnable = prompt | llm.bind_tools(tools)

    def call_model(
        state: dict,
        config: RunnableConfig,
    ):
        response = model_runnable.invoke(state, config)
        return {"messages": [response]}

    async def acall_model(state: dict, config: RunnableConfig):
        response = await model_runnable.ainvoke(state, config)
        return {"messages": [response]}

    graph = StateGraph(state_schema)
    graph.add_node("agent", RunnableLambda(call_model, acall_model))
    graph.add_node("tools", CustomToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        tools_condition,
    )
    graph.add_edge("tools", "agent")
    app = graph.compile()

    return Node(
        name=name,
        runnable=(
            app
            | RunnableLambda(
                lambda x: {
                    "messages": [
                        HumanMessage(content=x["messages"][-1].content, name=name)
                    ]
                }
            )
        ),
    )
