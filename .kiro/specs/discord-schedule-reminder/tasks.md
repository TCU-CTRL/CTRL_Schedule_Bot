# Implementation Plan

## Tasks

- [x] 1. プロジェクト基盤セットアップ
- [x] 1.1 Pythonプロジェクト構成を作成する
  - requestsライブラリを依存関係として追加
  - 環境変数読み込み用のconfigモジュールを準備
  - DISCORD_TOKEN、SCHEDULE_CHANNEL_ID、REMINDER_CHANNEL_IDの環境変数を定義
  - _Requirements: NFR-1.1, NFR-2.1, NFR-2.2_

- [x] 2. Discord API通信機能を構築する
- [x] 2.1 (P) チャンネルメッセージ取得機能を実装する
  - Bot Tokenを使用したHTTP認証ヘッダーを設定
  - 指定チャンネルから最新50件のメッセージを取得
  - API呼び出し失敗時のエラーハンドリングとログ出力
  - _Requirements: 1.1, NFR-1.3, NFR-3.2_
  - _Contracts: DiscordClient.get_messages()_

- [x] 2.2 (P) リマインドメッセージ送信機能を実装する
  - 指定チャンネルにテキストメッセージを送信
  - 送信成功・失敗の結果を返却
  - _Requirements: 2.3, NFR-1.3_
  - _Contracts: DiscordClient.post_message()_

- [x] 3. 予定解析機能を構築する
- [x] 3.1 メッセージから予定情報を抽出する機能を実装する
  - `M/D 活動内容` 形式の正規表現パターンでマッチング
  - 月・日・活動内容を抽出してデータ構造に変換
  - 年をまたぐ場合の処理（12月に1月の予定があるケース）
  - パース失敗時はNoneを返却しログを出力
  - _Requirements: 1.2, NFR-3.1_
  - _Contracts: ScheduleParser.parse_schedule()_

- [x] 4. 日付計算機能を構築する
- [x] 4.1 リマインド対象日を計算する機能を実装する
  - 金曜日実行時は次週水曜日（5日後）を返却
  - 月曜日実行時は今週水曜日（2日後）を返却
  - それ以外の曜日はNoneを返却（リマインド不要）
  - _Requirements: 1.3, 2.1, 2.2_
  - _Contracts: DateCalculator.get_target_date(), DateCalculator.is_reminder_day()_

- [x] 5. リマインドメッセージ整形機能を構築する
- [x] 5.1 活動予定を見やすい形式に整形する機能を実装する
  - 絵文字付きのヘッダー「📅 今週の活動予定」を生成
  - 日付を「M/D（曜日）」形式で表示
  - 活動内容と準備を促すメッセージを含める
  - _Requirements: 2.4_
  - _Contracts: MessageFormatter.format_reminder()_

- [x] 6. リマインド送信オーケストレーションを構築する
- [x] 6.1 全体フローを制御するメイン処理を実装する
  - 予定チャンネルからメッセージを取得
  - 各メッセージをパースして予定情報を抽出
  - 今日がリマインド日か判定し、対象日を計算
  - 対象日に該当する予定があればリマインドを送信
  - 該当予定がなければ送信をスキップしログ出力
  - _Requirements: 2.1, 2.2, 3.2_
  - _Contracts: ReminderSender.run()_

- [x] 7. GitHub Actions定期実行を設定する
- [x] 7.1 ワークフローファイルを作成する
  - 金曜日と月曜日の指定時刻にcronトリガーを設定
  - Python実行環境とrequestsのインストールステップを追加
  - GitHub SecretsからDISCORD_TOKENとチャンネルIDを環境変数として渡す
  - メインスクリプトを実行するステップを追加
  - _Requirements: 3.1, NFR-1.2, NFR-2.2_

- [x] 8. 単体テストを作成する
- [x] 8.1 (P) 予定解析機能のテストを作成する
  - 正常形式（3/20 練習試合）のパース成功
  - 不正形式（日付なし、形式違い）のパース失敗
  - 境界値（月末、年末年始）の処理確認
  - _Requirements: 1.2, NFR-3.1_

- [x] 8.2 (P) 日付計算機能のテストを作成する
  - 金曜日に実行した場合の次週水曜日計算
  - 月曜日に実行した場合の今週水曜日計算
  - その他の曜日でNone返却の確認
  - _Requirements: 1.3, 2.1, 2.2_

- [x] 8.3 (P) メッセージ整形機能のテストを作成する
  - 出力フォーマットの確認
  - 絵文字と曜日表示の正確性
  - _Requirements: 2.4_

## Requirements Coverage

| Requirement | Task |
|-------------|------|
| 1.1 | 2.1 |
| 1.2 | 3.1, 8.1 |
| 1.3 | 4.1, 8.2 |
| 2.1 | 4.1, 6.1, 8.2 |
| 2.2 | 4.1, 6.1, 8.2 |
| 2.3 | 2.2 |
| 2.4 | 5.1, 8.3 |
| 3.1 | 7.1 |
| 3.2 | 6.1 |
| NFR-1.1 | 1.1 |
| NFR-1.2 | 7.1 |
| NFR-1.3 | 2.1, 2.2 |
| NFR-2.1 | 1.1 |
| NFR-2.2 | 1.1, 7.1 |
| NFR-3.1 | 3.1, 8.1 |
| NFR-3.2 | 2.1 |
