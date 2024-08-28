from typing import Any, List, Literal, Optional, Tuple, Union, cast

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    InvalidToolCall,
    ToolCall,
    ToolMessage,
)
from langgraph.prebuilt.tool_node import INVALID_TOOL_NAME_ERROR_TEMPLATE, ToolNode


class CustomToolNode(ToolNode):
    def _parse_input(
        self, input: Union[list[AnyMessage], dict[str, Any]]
    ) -> Tuple[List[ToolCall | InvalidToolCall], Literal["list", "dict"]]:
        if isinstance(input, list):
            output_type = "list"
            message: AnyMessage = input[-1]
        elif messages := input.get("messages", []):
            output_type = "dict"
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        if not isinstance(message, AIMessage):
            raise ValueError("Last message is not an AIMessage")

        tool_calls = [
            self._inject_state(call, input)
            for call in cast(AIMessage, message).tool_calls
        ]

        tool_calls += [call for call in cast(AIMessage, message).invalid_tool_calls]

        return tool_calls, output_type

    def _validate_tool_call(
        self, call: ToolCall | InvalidToolCall
    ) -> Optional[ToolMessage]:
        if "error" in call:
            return ToolMessage(
                "invalid JSON arguments.",
                name=call["name"],
                tool_call_id=call["id"],
            )

        if (requested_tool := call["name"]) not in self.tools_by_name:
            content = INVALID_TOOL_NAME_ERROR_TEMPLATE.format(
                requested_tool=requested_tool,
                available_tools=", ".join(self.tools_by_name.keys()),
            )
            return ToolMessage(content, name=requested_tool, tool_call_id=call["id"])
        else:
            return None


def tools_condition(
    state: Union[list[AnyMessage], dict[str, Any]],
) -> Literal["tools", "__end__"]:
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    elif (
        hasattr(ai_message, "invalid_tool_calls")
        and len(ai_message.invalid_tool_calls) > 0
    ):
        return "tools"
    return "__end__"
