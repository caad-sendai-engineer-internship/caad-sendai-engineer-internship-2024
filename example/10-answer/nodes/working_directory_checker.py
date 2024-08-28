import os

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

from nodes.base import Node


def create_working_directory_checker_node(
    working_directory: str, name: str = "WorkingDirectoryChecker"
) -> Node:
    def node(state, config) -> dict:
        thread_id = config["configurable"]["thread_id"]
        if thread_id == "":
            thread_id = "default"

        thread_working_directory = f"{working_directory}/{thread_id}"
        if not os.path.exists(thread_working_directory):
            os.makedirs(thread_working_directory)
        thread_working_directory_files = [
            f for f in os.listdir(thread_working_directory)
        ]

        messages = None

        pre_files = set(state["working_directory_files"] or [])
        post_files = set(thread_working_directory_files)
        new_files = sorted(list(post_files - pre_files))
        if new_files:
            if not state["messages"][-1].name:
                messages = f"ユーザーがアップロードしたファイルをカレントディレクトリに保存しました。:\n{"\n".join([f" - {f}" for f in new_files])}"
            else:
                messages = f"会話によってカレントディレクトリにファイルが生成されたのを確認しました。:\n{"\n".join([f" - {f}" for f in new_files])}"

        if not state["messages"][-1].name:
            next = "agent"
        else:
            next = "end"

        result = {
            "working_directory": thread_working_directory,
            "working_directory_files": thread_working_directory_files,
            "working_directory_files_message": "\n".join(
                [f" - {f}" for f in sorted(thread_working_directory_files)]
            ),
            "next": next,
        }

        if messages:
            result["messages"] = [HumanMessage(content=messages, name=name)]

        return result

    return Node(name=name, runnable=RunnableLambda(node))
