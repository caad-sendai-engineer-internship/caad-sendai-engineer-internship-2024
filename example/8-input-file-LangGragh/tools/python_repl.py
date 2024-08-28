import os
from contextlib import contextmanager
from typing import Annotated, Type

import japanize_matplotlib  # noqa
import matplotlib
import pandas as pd
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool, ToolException
from langchain_experimental.utilities import PythonREPL
from langgraph.prebuilt import InjectedState
from matplotlib import pyplot as plt

pd.set_option("display.float_format", "{:.2f}".format)
pd.set_option("display.max_columns", 10000)

matplotlib.use("agg")

plt.rcParams.update(
    {
        "figure.figsize": (16, 9),  # 図のサイズ
        "figure.dpi": 100,  # 解像度
        "axes.titlesize": 18,  # タイトルのフォントサイズ
        "axes.labelsize": 14,  # 軸ラベルのフォントサイズ
        "axes.grid": True,  # グリッドを表示
        "grid.alpha": 0.7,  # グリッドの透明度
        "grid.linestyle": "--",  # グリッドのスタイル
        "lines.linewidth": 2.0,  # 線の太さ
        "lines.markersize": 8,  # マーカーのサイズ
        "xtick.labelsize": 12,  # x軸の目盛りラベルのフォントサイズ
        "ytick.labelsize": 12,  # y軸の目盛りラベルのフォントサイズ
        "legend.fontsize": 12,  # 凡例のフォントサイズ
        "legend.loc": "best",  # 凡例の位置
        "axes.spines.top": False,  # 上部の枠線を非表示
        "axes.spines.right": False,  # 右部の枠線を非表示
        "axes.spines.left": True,  # 左部の枠線を表示
        "axes.spines.bottom": True,  # 下部の枠線を表示
        "axes.axisbelow": True,  # グリッドを軸の下に表示
        "axes.formatter.useoffset": False,  # オフセットを無効化
        "axes.formatter.use_locale": False,  # ロケールを使用しない
        "axes.formatter.use_mathtext": True,  # LaTeXスタイル
        "axes.formatter.limits": (-10, 10),  # この範囲で指数表記を避ける
    }
)

plt.style.use("ggplot")


@contextmanager
def change_dir(working_directory: str):
    original_path = os.getcwd()
    try:
        os.chdir(working_directory)
        yield
    finally:
        os.chdir(original_path)


class PythonReplInput(BaseModel):
    code: str = Field(description="実行するPythonコード。")
    is_secure: bool = Field(
        description="セキュリティを確保するために、このコードが安全であることを確認します。"
    )
    state: Annotated[dict, InjectedState]


class PythonReplTool(BaseTool):
    name: str = "python_execution"
    description: str = "これを使用して Python コードを実行します。値の出力を確認したい場合は、`print(...)` で出力する必要があります。これはユーザーに表示されます。"
    args_schema: Type[BaseModel] = PythonReplInput
    handle_tool_error: bool = True
    handle_validation_error: bool = True

    def _run(
        self,
        code: str,
        is_secure: bool,
        state: dict,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        with change_dir(state["working_directory"]):
            try:
                if not is_secure:
                    raise ToolException("セキュアでないコードは実行できません。")
                if "plt.show(" in code:
                    raise ToolException(
                        "plt.show() は実行できません。ファイルで出力してください。"
                    )
                repl = PythonREPL()
                repl.locals = repl.globals
                result = repl.run(code)
            except Exception as e:
                raise ToolException(f"Failed to execute. Error: {repr(e)}")
            return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
