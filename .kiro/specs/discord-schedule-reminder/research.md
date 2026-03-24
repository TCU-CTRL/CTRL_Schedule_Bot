# Research & Design Decisions

## Summary
- **Feature**: `discord-schedule-reminder`
- **Discovery Scope**: New Feature（グリーンフィールド）
- **Key Findings**:
  - discord.py 2.6.x が安定版として利用可能、`channel.history()` でメッセージ取得可能
  - メッセージ読み取りにはBot Token + Gateway接続が必要（Webhookは送信専用）
  - GitHub Actionsのcronは正確ではないが、週次リマインドには十分な精度

## Research Log

### Discord API: メッセージ取得方法
- **Context**: 予定チャンネルからメッセージを取得する方法の調査
- **Sources Consulted**:
  - [discord.py API Reference](https://discordpy.readthedocs.io/en/stable/api.html)
  - [Discord Channel Messages Scraper](https://apify.com/felt/discord-message-scraper/api/python)
- **Findings**:
  - `channel.history(limit=N)` でメッセージ取得可能
  - 100件/リクエストの制限あり、レート制限は100リクエスト/分/ルート
  - `before`, `after`, `around` パラメータで時間フィルタリング可能
  - discord.py 2.6.4 が2025年10月リリースの最新安定版
- **Implications**:
  - Bot TokenとGateway接続が必要（メッセージ読み取りのため）
  - GitHub Actionsでは常時接続が困難 → HTTP API直接利用を検討

### Discord: Webhook vs Bot Token
- **Context**: リマインド送信方法の選択
- **Sources Consulted**:
  - [Discord Webhooks Guide 2025](https://inventivehq.com/blog/discord-webhooks-guide)
  - [Discord Webhook Resource](https://discord.com/developers/docs/resources/webhook)
- **Findings**:
  - Webhook: 送信専用、認証不要、30リクエスト/分制限
  - Bot Token: 双方向通信可能、メッセージ読み取りにはGateway必要
  - HTTP interaction bot: Slash commands対応、Webhookより柔軟
- **Implications**:
  - メッセージ読み取り → Bot Token + HTTP API（REST）
  - リマインド送信 → Webhook（シンプル）またはBot Token（統一性）
  - **選択**: Bot Token一本化でシンプルに

### GitHub Actions: Cron実行
- **Context**: 定期実行の信頼性確認
- **Sources Consulted**:
  - [GitHub Actions Discord Bot Tutorial](https://github.com/PhantomInsights/actions-bot)
  - [Discord Cron Bot](https://github.com/peterthehan/discord-cron-bot)
- **Findings**:
  - 月2,000分の無料枠あり
  - cron精度は不正確（数分のずれあり）
  - Secretsで認証情報の安全な管理可能
- **Implications**:
  - 週次リマインドには十分な精度
  - DISCORD_TOKEN、CHANNEL_IDはSecretsで管理

### Discord REST API: メッセージ取得（Bot Token利用）
- **Context**: Gateway接続なしでメッセージを取得する方法
- **Sources Consulted**: Discord Developer Documentation
- **Findings**:
  - `GET /channels/{channel.id}/messages` エンドポイントで取得可能
  - Bot Tokenを`Authorization: Bot {token}`ヘッダーで送信
  - discord.pyなしでrequestsライブラリで直接呼び出し可能
- **Implications**:
  - GitHub Actionsで軽量実行可能（Gateway不要）
  - シンプルなHTTPリクエストで実装可能

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| discord.py + Gateway | 常時接続Bot | 全機能利用可能 | GitHub Actionsで常時接続不可 | 不採用 |
| HTTP API直接 | REST APIのみ使用 | 軽量、サーバーレス対応 | 一部機能制限 | **採用** |
| Webhook送信のみ | 送信専用 | 最軽量 | メッセージ読み取り不可 | 不採用 |

## Design Decisions

### Decision: Discord API接続方式
- **Context**: GitHub ActionsでDiscordメッセージの読み取りと送信が必要
- **Alternatives Considered**:
  1. discord.py + Gateway接続 — 全機能利用可能だが常時接続必要
  2. Discord REST API + requests — 軽量、必要な機能のみ
  3. Webhook送信 + 手動予定管理 — 自動読み取り不可
- **Selected Approach**: Discord REST API + requestsライブラリ
- **Rationale**: GitHub Actionsの実行時間制限内で完結、依存関係最小
- **Trade-offs**: Gateway専用機能（リアルタイム通知等）は利用不可
- **Follow-up**: Bot作成とIntents設定の確認

### Decision: 日付パース方式
- **Context**: `M/D 活動内容` 形式のパース
- **Alternatives Considered**:
  1. 正規表現 — シンプル、依存なし
  2. dateutil.parser — 柔軟だが依存追加
- **Selected Approach**: 正規表現（`r'(\d{1,2})/(\d{1,2})\s+(.+)'`）
- **Rationale**: 形式が固定のため正規表現で十分
- **Trade-offs**: 形式変更時は正規表現の修正必要

### Decision: リマインド判定ロジック
- **Context**: 金曜日と月曜日に次の水曜日の予定をチェック
- **Selected Approach**:
  - 金曜日実行: 次週水曜日（5日後）の予定をチェック
  - 月曜日実行: 今週水曜日（2日後）の予定をチェック
- **Rationale**: 曜日ベースの単純な日付計算で実装可能

## Risks & Mitigations
- **Risk 1**: Discord APIレート制限超過 → メッセージ取得を最新N件に制限（50件程度）
- **Risk 2**: 予定形式のパースエラー → エラーハンドリングとログ出力で対応
- **Risk 3**: GitHub Actions cron精度のずれ → 週次実行では問題なし、時間クリティカルでない

## References
- [discord.py API Reference](https://discordpy.readthedocs.io/en/stable/api.html) — メッセージ取得API
- [Discord Webhooks Guide 2025](https://inventivehq.com/blog/discord-webhooks-guide) — Webhook vs Bot比較
- [GitHub Actions Discord Bot Tutorial](https://github.com/PhantomInsights/actions-bot) — cron実行の参考実装
- [Discord Developer Documentation](https://discord.com/developers/docs/resources/webhook) — 公式Webhook仕様
