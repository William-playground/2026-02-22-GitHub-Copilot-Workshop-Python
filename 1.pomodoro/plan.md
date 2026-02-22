# ポモドーロタイマー — 段階的実装計画

UIモック・architecture.md・features.md をもとに、動作確認しながら進められる粒度で実装ステップを整理する。

---

## Step 1: プロジェクト骨格の作成

**目標:** アプリが起動し、空のHTMLページが表示される状態にする

- [ ] `requirements.txt` の作成
- [ ] `requirements-dev.txt` の作成
- [ ] `.env` の作成（`FLASK_DEBUG=1`, `DATABASE_URL=sqlite:///pomodoro.db`）
- [ ] `app.py` の作成（`create_app()` ファクトリ、`GET /` ルートのみ）
- [ ] `templates/index.html` の作成（空のHTMLボイラープレート）
- [ ] Flask 起動確認（`flask run`）

**完了の定義:** `http://localhost:5000` にアクセスしてHTMLが返ること

---

## Step 2: タイマーUI の静的実装

**目標:** UIモックの見た目をHTMLとCSSだけで再現する（動作なし）

- [ ] `static/css/style.css` の作成
  - 背景色：青紫グラデーション（`#6c63ff` 系）
  - ウィンドウカード：白・角丸・シャドウ
  - タイトルバー風のレイアウト（「ポモドーロタイマー」「－ □ ×」）
- [ ] `index.html` の更新
  - モードラベル（「作業中」）
  - SVG 円形プログレスリング（静的・固定値）
  - 残り時間テキスト（「25:00」固定）
  - 「開始」ボタン（青紫・角丸）
  - 「リセット」ボタン（アウトライン）
  - 「今日の進捗」カード（「4 完了」「1時間40分 集中時間」固定値）

**完了の定義:** UIモック画像と同等の見た目がブラウザで確認できること

---

## Step 3: タイマーロジックの実装（JS）

**目標:** カウントダウンが動作し、ボタン操作ができる状態にする

- [ ] `static/js/timer.js` の作成（`PomodoroTimer` クラス）
  - コンストラクタ: `onTick(remainingSeconds)`, `onComplete()` コールバックを受け取る
  - `start(durationSeconds)`: `setInterval` でカウントダウン開始
  - `pause()`: `clearInterval` で一時停止
  - `reset(durationSeconds)`: 残り時間を初期値に戻す
  - DOM への参照を一切持たない（テスト可能な純粋クラス）
- [ ] `static/js/main.js` の作成
  - `PomodoroTimer` インスタンスを生成
  - 「開始」ボタン押下 → `timer.start()` 呼び出し
  - 「一時停止」ボタン（開始後に切替表示） → `timer.pause()`
  - 「リセット」ボタン → `timer.reset()`
  - `onTick`: 残り時間テキストと SVG リングを更新
  - `onComplete`: 終了音を再生

**完了の定義:** ブラウザ上でカウントダウンが動作し、開始・一時停止・リセットができること

---

## Step 4: 円形プログレスリングのアニメーション

**目標:** 残り時間に応じてリングが動的に減るようにする

- [ ] SVG `<circle>` の `stroke-dashoffset` を JS から更新する実装
  - `stroke-dasharray` = 円周長（固定値）
  - `stroke-dashoffset` = 円周長 × (残り秒 / 総秒数)
- [ ] `main.js` の `onTick` コールバック内でリングの offset を更新
- [ ] リングの色設定
  - 背景トラック：ライトグレー（`#e5e7eb`）
  - 進行リング：青紫（`#6c63ff`）

**完了の定義:** タイマー動作中にリングがスムーズに減ることが確認できること

---

## Step 5: モード切替の実装（JS）

**目標:** ポモドーロ・短い休憩・長い休憩を切り替えられるようにする

- [ ] モード定数の定義（`MODES = { pomodoro: 1500, short_break: 300, long_break: 900 }`）
- [ ] モードラベルの更新（「作業中」「短い休憩」「長い休憩」）
- [ ] タイマー完了時に連続ポモドーロ数をカウント
- [ ] 4回完了後に長い休憩を自動提案（`confirm()` ダイアログまたはUIメッセージ）
- [ ] ブラウザタブタイトルへの残り時間反映（`document.title = \`\${time} — \${mode}\``）

**完了の定義:** 3種類のモードが切り替わり、それぞれ正しい時間でカウントダウンが始まること

---

## Step 6: DB モデルとリポジトリ層の実装（Python）

**目標:** セッションデータを SQLite に保存・取得できる状態にする

- [ ] `models/session.py` の作成
  - `Session` モデル（`id`, `type`, `started_at`, `completed_at`）
- [ ] `repositories/session_repository.py` の作成
  - `AbstractSessionRepository` 抽象クラス（`save`, `count_today`, `get_today_focus_minutes`, `count_total`）
  - `SQLiteSessionRepository` の実装
- [ ] `app.py` の `create_app()` に `db.init_app()` と `db.create_all()` を追加

**完了の定義:** `flask shell` でセッションを手動保存・取得できること

---

## Step 7: ビジネスロジック層の実装（Python）

**目標:** SessionService を実装し、Flask から呼び出せる状態にする

- [ ] `services/session_service.py` の作成
  - `complete_session(session_type)` → 保存 + 今日の統計を返す
  - `get_stats()` → `today_count`, `today_focus_minutes`, `total_count` を返す
- [ ] `SessionService` は `AbstractSessionRepository` に依存（DI）

**完了の定義:** `SessionService` を単体でインスタンス化して動作確認できること

---

## Step 8: REST API の実装（Flask）

**目標:** フロントエンドからセッション記録・統計取得ができる状態にする

- [ ] `POST /api/session` ルートの実装
  - リクエスト: `{ "type": "pomodoro" }`
  - `SessionService.complete_session()` を呼び出して結果を返す
- [ ] `GET /api/stats` ルートの実装
  - `SessionService.get_stats()` を呼び出して統計を返す
- [ ] `main.js` の更新
  - タイマー完了時に `POST /api/session` を `fetch` で呼び出す
  - ページ読み込み時に `GET /api/stats` を取得して進捗カードを更新

**完了の定義:** タイマーを完了すると「今日の進捗」カードの数値が更新されること

---

## Step 9: テストの実装

**目標:** 主要なロジックのテストが pass する状態にする

- [ ] `tests/conftest.py` の作成（インメモリ SQLite フィクスチャ）
- [ ] `tests/test_session_service.py` の作成
  - `FakeSessionRepository` を使ったセッション完了テスト
  - 統計集計ロジックのテスト
- [ ] `tests/test_session_repository.py` の作成
  - インメモリ SQLite に対する CRUD テスト
- [ ] `tests/test_routes.py` の作成
  - `POST /api/session` の正常系・異常系テスト
  - `GET /api/stats` のレスポンス形式テスト
- [ ] `pytest --cov` でカバレッジを確認

**完了の定義:** `pytest` がすべて pass し、カバレッジ 80% 以上を達成していること

---

## Step 10: UX 仕上げ

**目標:** 実用的な使い心地に仕上げる

- [ ] 終了音ファイル（`static/audio/bell.mp3`）の配置
- [ ] ブラウザ通知 API によるタイマー終了通知
- [ ] タイマー動作中にページを離れる場合の確認ダイアログ（`beforeunload`）
- [ ] キーボードショートカット（スペースキーで開始/一時停止）
- [ ] レスポンシブ対応（モバイル表示の確認）

**完了の定義:** 一連のポモドーロセッションを違和感なく実施できること

---

## 実装ステップの依存関係

```
Step 1  骨格作成
   ↓
Step 2  静的UI
   ↓
Step 3  タイマーロジック（JS）
   ↓
Step 4  プログレスリング
   ↓
Step 5  モード切替
   │
   ├── Step 6  DB モデル・リポジトリ
   │      ↓
   │   Step 7  SessionService
   │      ↓
   │   Step 8  REST API ← Step 5 と合流（フロントエンド連携）
   │      ↓
   │   Step 9  テスト
   │
   └── Step 10  UX 仕上げ（Step 8 完了後に並行して実施可能）
```

---

## 各ステップの目安工数

| Step | 内容 | 目安 |
|---|---|---|
| 1 | 骨格作成 | 15 分 |
| 2 | 静的UI | 30 分 |
| 3 | タイマーロジック | 30 分 |
| 4 | プログレスリング | 20 分 |
| 5 | モード切替 | 20 分 |
| 6 | DB モデル・リポジトリ | 30 分 |
| 7 | SessionService | 20 分 |
| 8 | REST API | 20 分 |
| 9 | テスト | 40 分 |
| 10 | UX 仕上げ | 30 分 |
| **合計** | | **約 4 時間** |
