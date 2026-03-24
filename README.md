# CTRL_Schedule_Bot

部活動のスケジュールリマインダーBot。Discordの予定チャンネルから活動日を読み取り、自動でリマインド通知を送信します。

## 背景

毎週の活動前に手動でリマインドを送信するのが負担になっていました。特に:
- 金曜日に「今週水曜は活動日です」と告知を忘れがち
- 月曜日の最終リマインドも忘れることがある
- 毎回同じ作業を繰り返すのが面倒

このBotで予定の告知作業を完全自動化し、運営の負担を軽減します。

## 機能

- 予定チャンネルから `M/D 活動内容` 形式のメッセージを自動解析
- 前週金曜日と当週月曜日の2回、@everyone付きでリマインド送信
- GitHub Actionsによる完全自動化（サーバーレス運用）

## セットアップ

### 1. Discord Botの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成
2. Bot設定で以下を有効化:
   - `MESSAGE CONTENT INTENT`（メッセージ内容の読み取りに必要）
3. Bot Tokenをコピー

### 2. Botをサーバーに招待

OAuth2 URL Generatorで以下の権限を選択:
- `bot` スコープ
- `Send Messages` 権限
- `Read Message History` 権限

### 3. 環境変数の設定

```bash
# ローカル開発用（.envファイル）
DISCORD_TOKEN=your_bot_token
SCHEDULE_CHANNEL_ID=予定チャンネルのID
REMINDER_CHANNEL_ID=リマインド送信先チャンネルのID
```

チャンネルIDの取得方法:
1. Discordの設定 → 詳細設定 → 開発者モードを有効化
2. チャンネルを右クリック → 「IDをコピー」

### 4. GitHub Secretsの設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定:
- `DISCORD_TOKEN`
- `SCHEDULE_CHANNEL_ID`
- `REMINDER_CHANNEL_ID`

## 使い方

### 予定の投稿形式

予定チャンネルに以下の形式でメッセージを投稿:

```
3/25 ゲームジャム
4/2 練習試合
4/9 定例会
```

### ローカルでのテスト

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 接続テスト（予定チャンネルのメッセージを読み取り）
python main.py --test connection

# テストメッセージ送信
python main.py --test send

# リマインド送信（最も近い予定を@everyone付きで送信）
python main.py --test force

# ドライラン（送信せずにシミュレーション）
python main.py --test dry-run
```

### GitHub Actionsでの実行

#### 手動実行
1. Actions タブを開く
2. "Schedule Reminder" ワークフローを選択
3. "Run workflow" をクリック

#### 自動実行の有効化
部長の承認後、`.github/workflows/reminder.yml` のコメントアウトを解除:

```yaml
on:
  schedule:
    # 金曜日 18:00 JST (09:00 UTC)
    - cron: '0 9 * * 5'
    # 月曜日 09:00 JST (00:00 UTC)
    - cron: '0 0 * * 1'
  workflow_dispatch:
```

## リマインドメッセージ例

```
@everyone
📅 今週の活動予定
日付: 3/25（水）
内容: ゲームジャム

準備をお願いします！
```

## プロジェクト構成

```
CTRL_Schedule_Bot/
├── main.py                 # エントリーポイント
├── requirements.txt        # 依存関係
├── src/
│   ├── config.py           # 環境変数の読み込み
│   ├── discord_client.py   # Discord API通信
│   ├── schedule_parser.py  # 予定メッセージの解析
│   ├── date_calculator.py  # リマインド日の計算
│   ├── message_formatter.py# リマインドメッセージの整形
│   └── reminder_sender.py  # リマインド送信のオーケストレーション
├── tests/                  # ユニットテスト
└── .github/workflows/      # GitHub Actions設定
```

## テスト

```bash
# 全テスト実行
pytest -v

# カバレッジ付き
pytest --cov=src
```

## 技術スタック

- Python 3.11+
- requests（Discord REST API通信）
- GitHub Actions（定期実行）
- pytest（テスト）
