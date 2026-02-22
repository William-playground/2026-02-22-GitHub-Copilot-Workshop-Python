# フロントエンド仕様

> **実装状況:** 現時点では `templates/index.html` のみ存在する。`static/css/` および `static/js/` ディレクトリは未作成。

---

## 現在の実装

### `templates/index.html`

アプリのメイン画面。現在はプレースホルダーのみ。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポモドーロタイマー</title>
</head>
<body>
    <h1>ポモドーロタイマー</h1>
    <p>準備中...</p>
</body>
</html>
```

- Flask の `render_template("index.html")` によって `GET /` で配信される
- CSS・JavaScript の読み込みは未実装

---

## 未実装コンポーネント（設計済み）

### スタイルシート (`static/css/style.css`)（未実装）

| 要素 | 設計値 |
|---|---|
| 背景色 | 青紫グラデーション（`#6c63ff` 系） |
| カード | 白・角丸・シャドウ |
| 進行リング（アクティブ） | `#6c63ff` |
| 進行リング（背景トラック） | `#e5e7eb`（ライトグレー） |

---

### タイマーロジック (`static/js/timer.js`)（未実装）

DOM に非依存な純粋クラス `PomodoroTimer`。

**設計インターフェース**

```javascript
class PomodoroTimer {
    /**
     * @param {function(number): void} onTick - 毎秒呼ばれるコールバック（引数: 残り秒数）
     * @param {function(): void} onComplete - タイマー終了時のコールバック
     */
    constructor(onTick, onComplete) { ... }

    /** カウントダウン開始 */
    start(durationSeconds) { ... }

    /** 一時停止 */
    pause() { ... }

    /** 残り時間を初期値にリセット */
    reset(durationSeconds) { ... }
}
```

- `setInterval`（1 秒間隔）でカウントダウンを管理
- DOM 参照を持たないため Jest での単体テストが可能

---

### DOM 操作 (`static/js/main.js`)（未実装）

`PomodoroTimer` を利用して UI を制御する。

**主な責務**

| 処理 | 説明 |
|---|---|
| ボタン操作 | 「開始」→ `timer.start()`, 「一時停止」→ `timer.pause()`, 「リセット」→ `timer.reset()` |
| 残り時間表示 | `onTick` で `MM:SS` 形式のテキストを更新 |
| 円形プログレスリング | `onTick` で SVG `stroke-dashoffset` を更新 |
| 終了処理 | `onComplete` で終了音再生・API 呼び出し（`POST /api/session`） |
| 統計表示 | ページ読み込み時に `GET /api/stats` を取得して進捗カードを更新 |
| タブタイトル | 残り時間をブラウザタブタイトルに反映（例: `25:00 — 作業中`） |

---

## タイマーモード

| モード | 定数名 | デフォルト時間 |
|---|---|---|
| ポモドーロ | `pomodoro` | 25 分（1500 秒） |
| 短い休憩 | `short_break` | 5 分（300 秒） |
| 長い休憩 | `long_break` | 15 分（900 秒） |

4 回のポモドーロ完了後に長い休憩を自動提案する。

---

## UIコンポーネント（予定）

| コンポーネント | 説明 |
|---|---|
| モードラベル | 現在のモード名を表示（「作業中」「短い休憩」「長い休憩」） |
| 残り時間テキスト | `MM:SS` 形式でカウントダウンを表示 |
| 円形プログレスリング | SVG `<circle>` の `stroke-dashoffset` で残り時間を視覚化 |
| 開始/一時停止ボタン | タイマー状態に応じてラベルが切り替わる |
| リセットボタン | 現在のモードの初期時間に戻す |
| 今日の進捗カード | 完了セッション数・累計集中時間を表示 |
