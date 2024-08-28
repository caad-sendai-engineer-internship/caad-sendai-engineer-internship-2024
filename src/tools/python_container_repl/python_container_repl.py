import os
import unicodedata
from typing import Annotated, Iterable, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool, ToolException
from langgraph.prebuilt import InjectedState
from python_on_whales import docker

PYTHON_REPL_IMAGE = "python_repl:latest"
IMAGE_WORKDIR = "/sandbox"
IMAGE_SETUP_DIR = "/.setup"


class PythonContainerReplInput(BaseModel):
    code: str = Field(description="実行するPythonコード。")
    is_secure: bool = Field(
        description="セキュリティを確保するために、このコードが安全であることを確認します。"
    )
    state: Annotated[dict, InjectedState]


class PythonContainerReplTool(BaseTool):
    name: str = "python_container_repl"
    description: str = "\n".join(
        [
            "これを使用して Python コードを実行します。",
            "このツールは、Python コードを実行するためにコンテナを使用します。",
            "コンテナはツールを実行するたびに作成され、削除されます、そのため変数の状態は保持されません。",
            "カレントディレクトリは、ボリュームマウントされており、ファイルの読み書きが可能です。",
            "値の出力を確認したい場合は、`print(...)` で出力する必要があります、これはユーザーに表示されます。",
        ]
    )
    args_schema: Type[BaseModel] = PythonContainerReplInput
    handle_tool_error: bool = True
    handle_validation_error: bool = True

    def _run(
        self,
        code: str,
        is_secure: bool,
        state: dict,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        stdout = ""
        stderr = ""
        try:
            if not is_secure:
                raise ToolException("セキュアでないコードは実行できません。")

            if "plt.show(" in code:
                raise ToolException(
                    "plt.show() は実行できません。ファイルで出力してください。"
                )

            code = unicodedata.normalize("NFC", code)
            code = "\n".join(
                [
                    "import python_repl_setup",
                    code,
                ]
            )

            stream_run = docker.run(
                image=PYTHON_REPL_IMAGE,
                command=[code],
                remove=True,
                volumes=[
                    (
                        f"{os.getcwd()}/{state.get("working_directory")}",
                        IMAGE_WORKDIR,
                        "rw",
                    ),
                    (f"{os.path.dirname(__file__)}/setup", IMAGE_SETUP_DIR, "ro"),
                ],
                workdir=IMAGE_WORKDIR,
                stream=True,
            )

            if isinstance(stream_run, Iterable):
                for stream_type, stream_content in stream_run:
                    if isinstance(stream_content, bytes | bytearray):
                        stream_content = stream_content.decode()
                    if isinstance(stream_content, memoryview):
                        stream_content = stream_content.tobytes().decode()
                    if stream_type == "stdout":
                        stdout += stream_content
                    else:
                        stderr += stream_content
            else:
                stdout = stream_run

        except Exception as e:
            if stderr:
                return f"{stderr=}"

            raise ToolException(f"Failed to execute. Error: {repr(e)}")

        if not stdout:
            return "正常に実行されましたが、出力はありません。print(...)を使用することで出力を確認できます。"

        return f"{stdout=}"


def build_image():
    if docker.images(repository_or_tag=PYTHON_REPL_IMAGE):
        return

    docker.build(
        context_path=os.path.dirname(__file__),
        tags=PYTHON_REPL_IMAGE,
    )


build_image()
