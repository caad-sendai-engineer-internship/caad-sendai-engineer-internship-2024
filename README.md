# 2024年 シーエーアドバンス仙台　エンジニア職　インターンシップ
## はじめに
今回のインターンシップではLLMアプリケーションの開発を行います。  
下記の手順に沿ってPC環境の準備を行ってください。

### Githubの設定
下記参考に⑦まで進めてください。  
https://prog-8.com/docs/git-env  
※⑥はスキップで問題ないです。

### IDEについて
いつも利用しているものをインストールしてお使い頂いて構いません。

[VSCode](https://code.visualstudio.com/)については `.vscode` に設定例を記載しております。  
設定例では以下の拡張機能のインストールを前提としております。  
https://marketplace.visualstudio.com/items?itemName=ms-python.python
https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff

### Pythonパッケージ管理ツールのインストール
Pythonを実行できればパッケージツールや仮想環境を構築しなくでもOKです。  
個人の開発しやすい方法で進めてください。  
パッケージツールがあるとライブラリの依存関係を管理するのが楽になりますし  
仮想環境を準備するとプロジェクト毎にPythonのバージョンを変更したり、本体のPC環境を汚さずに開発できます。  

| ツール名 | パッケージインストール | パッケージ仮想化 | 依存関係の管理 | タスクランナー | パッケージ開発 |
| -------- | --------------------- | --------------- | -------------- | ------------- | ------------- |
| pip      | 〇                   | ×               | ×              | ×             | ×             |
| venv     | ×                   | 〇               | ×              | ×             | ×             |
| pip-tools| ×                   | ×               | 〇              | ×             | ×             |
| Pipenv   | 〇                   | 〇               | 〇              | 〇             | ×             |
| Poetry   | 〇                   | 〇               | 〇              | ×             | 〇             |
| PDM      | 〇                   | 〇               | 〇              | 〇             | 〇             |
| Rye      | 〇                   | 〇               | 〇              | 〇             | 〇             |

今回は参考としてRyeを使用します。

#### Ryeインストール
```Shell
curl -sSf https://rye.astral.sh/get | bash
```

#### PATHを通す
```Shell
echo 'source "$HOME/.rye/env"' >> ~/.zprofile
source ~/.zprofile
```

#### インストールの確認
```Shell
rye --version
rye 0.38.0
commit: 0.38.0 (3e3c8540f 2024-08-02)
platform: macos (aarch64)
self-python: cpython@3.12.3
symlink support: true
uv enabled: true
```

### サンプルコードのクローン
任意のディレクトリに移動（`cd`コマンド）して下記コマンドを実行してください。

```Shell
 git clone git@github.com:caad-sendai-engineer-internship/caad-sendai-engineer-internship-202409.git
```
プロジェクトのディレクトリに移動
```Shell
cd caad-sendai-engineer-internship-202409
```

### Pythonライブラリをインストール & 仮想環境を構築
```Shell
rye sync
```
`caad-sendai-engineer-internship-202409`ディレクトリ配下に下記のファイルとディレクトリが作成されます

- .venv
- .python-version
- pyproject.toml
- requirements-dev.lock
- requirements.lock

### 自分の作業ブランチを作成
`caad-sendai-engineer-internship-202409`ディレクトリ配下で下記コマンドを実行してください。
```Shell
git checkout -b feature/<自分の名前>
```

### 環境変数の設定
インターン中に使用する環境変数を設定してください。
```Shell
#Azure OpenAI
AZURE_OPENAI_ENDPOINT=""
OPENAI_API_VERSION=""
AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME=""
AZURE_OPENAI_CHAT_MODEL_MINI_DEPLOYMENT_NAME=""
AZURE_OPENAI_IMAGE_MODEL_DEPLOYMENT_NAME=""
AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME=""
AZURE_OPENAI_API_KEY=""

#LangSmith
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY=""
LANGCHAIN_PROJECT=""
```

環境変数は、特定のシステムまたはプロセスの環境設定を保持するための変数です。これらは、システムのセキュリティ設定、アプリケーションの設定、ユーザーの認証情報など、さまざまな情報を含む可能性があります。
環境変数が共有できない主な理由は以下の通りです。
1. **セキュリティ**: 環境変数は、データベースのパスワードやAPIキーのような機密情報を保持することがよくあります。これらの情報を共有すると、セキュリティリスクが生じ、不正アクセスやデータ漏洩の可能性があります。
2. **環境依存性**: 環境変数は、特定のシステムやアプリケーションの環境設定を保持します。したがって、これらの変数は、その環境特有の設定を含む可能性があり、他の環境で使用すると機能しないかもしれません。
3. **プロセスの隔離**: 各プロセスは独自の環境変数を持つため、一つのプロセスから別のプロセスへ環境変数を直接共有することはできません。これは、プロセス間の干渉を防ぎ、システムの安定性とセキュリティを保つための設計です。
   したがって、環境変数を共有する場合は、セキュリティを確保しつつ適切な方法を選ぶ必要があります。例えば、安全な設定管理ツールや秘密管理ツールを使用することで、環境変数を安全に共有することが可能です。


環境構築は以上です

## 開発中でGitHubにコードを反映する場合
`caad-sendai-engineer-internship-202409`ディレクトリ配下で下記コマンドを実行してください。

### 1 コードを変更した場合
```Shell
git add <file_name> or git add .
```
このコマンドは、変更したファイルをステージングエリアに追加します。ステージングエリアは、コミットする準備ができた変更を追跡する場所です。
これらのコマンドは、それぞれ全ての変更をステージングエリアに追加するか、特定のファイルのみを追加します。

### 2 コミットする場合
```Shell
git commit -m "コミットメッセージ"
```
このコマンドは、ステージングエリアに追加された変更をローカルリポジトリに保存します。各コミットは一意のIDを持ち、特定の変更を追跡することができます。
このコマンドは、ステージングエリアの変更をローカルリポジトリにコミットし、それにメッセージを付けます。

### 3 リモートリポジトリを更新する場合
```Shell
git push origin feature/<自分の名前>
```
このコマンドは、ローカルリポジトリの変更をリモートリポジトリ（例えばGitHub）に送信します。これにより、他の開発者があなたの変更を見ることができます。


## 開発中にPythonライブラリを追加・適応・削除する場合
### 特定のPythonライブラリをプロジェクトに追加したい場合
```Shell
rye add <ライブラリ名>
```

### 追加したPythonライブラリをプロジェクトに適応する場合
```Shell
rye sync
```

### 特定のPythonライブラリをプロジェクトから削除したい場合
```Shell
rye remove <ライブラリ名>
```

## 課題の成果物について
- ブランチを`feature/<自分の名前>`の名称で作成してプルリクエストを作成してください
- mainブランチへのコミットやマージは基本しないでください
- `src` ディレクトリ配下に完成形コードを入れてください
- 作業用のフォルダなどは不要です
- Secret情報を記載した.envファイルや課題データはコミットしないでください
- プルリクエストのdescriptionやコード上に苦戦したところとやアピールなどあれば記載してください

# 広告媒体情報
## データ項目説明
| 項目名 | 説明 | 計算式 |
| --- | --- | --- |
| 実績日 | 実績が発生した日付 |  |
| クライアントID | 社内管理しているクライアントのID |  |
| 企業名 | 社内管理しているクライアントの企業名 |  |
| サービス名 | 社内管理しているクライアントのサービス名 |  |
| 媒体ID | 社内管理している媒体のID |  |
| 媒体名 | 社内管理している媒体の名称 |  |
| アカウントID | アカウントのID |  |
| アカウント名 | アカウントの名称 |  |
| キャンペーンID | キャンペーンのID |  |
| キャンペーン名 | キャンペーンの名称 |  |
| 広告グループID | 広告グループのID |  |
| 広告グループ名 | 広告グループの名称 |  |
| 広告ID | 広告のID |  |
| 広告名 | 広告の名称 |  |
| 遷移先URL | 広告をクリックした時に遷移するURL |  |
| タイトル | 広告のテキストタイトル |  |
| 本文 | 広告のテキスト本文 |  |
| 画像URL | 広告の画像のURL |  |
| 動画URL | 広告の動画のURL |  |
| コスト | 広告配信の費用 |  |
| インプレッション | 広告の表示回数 |  |
| クリック | 広告のクリック回数 |  |
| CV | 広告の目標アクションの発生回数<br>Conversionの略 |  |
| CPM | 1000インプレッションあたりのコスト<br>Cost per Milleの略 | コスト ÷ インプレッション × 1000 |
| CTR | インプレッションのうちクリックされた回数の割合<br>Click Through Rateの略 | クリック ÷ インプレッション |
| CPC | クリックあたりのコスト<br>Cost Per Clickの略 | コスト ÷ クリック |
| CVR | クリックのうちCVされた回数の割合<br>Conversion Rateの略 | CV ÷ クリック |
| CPA | CVあたりのコスト<br>Cost Per Action | コスト ÷ CV |
| 動画視聴完了数 | 広告の動画が最後まで再生された回数 |  |

## 広告の基本構造
![広告の基本構造](https://github.com/user-attachments/assets/7e9cdada-123f-4485-99ce-55f840e2d2f7)
