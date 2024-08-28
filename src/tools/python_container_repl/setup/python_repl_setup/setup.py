import codecs  # noqa
import csv  # noqa
import json  # noqa
import os  # noqa

import japanize_matplotlib  # noqa
import magic  # noqa
import matplotlib
import numpy as np  # noqa
import pandas as pd
from matplotlib import pyplot as plt


def setup():
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


setup()
