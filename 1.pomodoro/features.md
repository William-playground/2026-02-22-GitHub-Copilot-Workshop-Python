# ポモドーロタイマー — 実装機能一覧

UIモック画像をもとに整理した実装対象機能の一覧。

---

## Phase 1: MVP（タイマーUI + コア機能）

### タイマー表示
- [ ] MM:SS 形式の残り時間を画面中央に大きく表示
- [ ] 円形プログレスリング（SVG arc）で残り時間を視覚的に表示
  - 残り時間に応じてリングが減っていくアニメーション
  - 進行中：青紫色（`#6c63ff` 系）/ 未経過：ライトグレー
- [ ] 現在のモードラベル表示（「作業中」「短い休憩」「長い休憩」）

### タイマー操作
- [ ] **開始** ボタン（押下でカウントダウン開始）
- [ ] **一時停止** ボタン（開始後に表示が切り替わる）
- [ ] **リセット** ボタン（現在のモードの初期時間に戻す）
- [ ] タイマー終了の検知（`remainingSeconds === 0` の判定）
- [ ] タイマー終了時の効果音再生（bell.mp3）

### モード管理
- [ ] ポモドーロ（25 分）
- [ ] 短い休憩（5 分）
- [ ] 長い休憩（15 分）
- [ ] 4 ポモドーロ完了後に長い休憩を自動提案

---

## Phase 2: データ記録・統計表示

### 今日の進捗カード（UIモック下部）
- [ ] 本日の完了セッション数を表示（例：「4 完了」）
- [ ] 本日の累計集中時間を表示（例：「1時間40分 集中時間」）
- [ ] ページ読み込み時に `/api/stats` から統計を取得して表示

### Flask REST API
- [ ] `GET /` — `index.html` の配信
- [ ] `POST /api/session` — セッション完了を記録
  - リクエスト: `{ "type": "pomodoro" | "short_break" | "long_break" }`
  - レスポンス: `{ "today_count": 4, "today_focus_minutes": 100 }`
- [ ] `GET /api/stats` — 統計データを返す
  - レスポンス: `{ "today_count": 4, "today_focus_minutes": 100, "total_count": 42 }`

### DB 層（SQLite）
- [ ] `sessions` テーブルの定義
  - カラム: `id`, `type`, `started_at`, `completed_at`
- [ ] 初回起動時のテーブル自動作成（`db.create_all()`）
- [ ] `AbstractSessionRepository` 抽象クラスの定義
- [ ] `SQLiteSessionRepository` の CRUD 実装

### ビジネスロジック（SessionService）
- [ ] セッション完了の保存
- [ ] 本日の完了セッション数の集計
- [ ] 本日の累計集中時間（分）の集計（pomodoro タイプのみ対象）
- [ ] 累計完了数の集計

---

## Phase 3: UX 向上・品質

### ブラウザ連携
- [ ] ブラウザのタブタイトルに残り時間を反映（例: `25:00 — 作業中`）
- [ ] ブラウザ通知 API（`Notification`）によるタイマー終了通知
- [ ] タイマー動作中にページを離れる場合の確認ダイアログ

### アクセシビリティ・細部
- [ ] ボタンの状態に応じたラベル切替（「開始」→「一時停止」）
- [ ] キーボードショートカット（スペースキーで開始/一時停止など）

---

## テスト

### Python バックエンド（pytest）
- [ ] `test_session_service.py` — Fake リポジトリを使った単体テスト
- [ ] `test_session_repository.py` — インメモリ SQLite を使った DB テスト
- [ ] `test_routes.py` — Flask テストクライアントを使った統合テスト

### JavaScript フロントエンド（Jest）
- [ ] `PomodoroTimer` クラスの単体テスト
  - start / pause / reset の動作検証
  - モード別の初期時間の検証
  - `onTick` / `onComplete` コールバックの呼び出し検証

---

## 設定・インフラ

- [ ] `requirements.txt` の作成（Flask, Flask-SQLAlchemy, python-dotenv）
- [ ] `requirements-dev.txt` の作成（pytest, pytest-cov, pytest-flask）
- [ ] `.env` による設定管理（DB パス、デバッグモードなど）
- [ ] `create_app()` ファクトリパターンの実装（テスト用設定の上書き対応）

---

## 優先実装順

```
Phase 1  タイマーUI + カウントダウン + 円形リング + 終了音
   ↓
Phase 2  Flask API + SQLite + セッション記録 + 統計カード表示
   ↓
Phase 3  ブラウザ通知 + タブタイトル + テスト整備
```
