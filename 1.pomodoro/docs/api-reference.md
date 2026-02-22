# API リファレンス

> **実装状況:** 現時点では `GET /` のみ実装済み。`POST /api/session` および `GET /api/stats` は未実装（`features.md` Phase 2 で予定）。

---

## 実装済みエンドポイント

### `GET /`

トップページの HTML を返す。

**レスポンス**

| 項目 | 値 |
|---|---|
| ステータスコード | `200 OK` |
| Content-Type | `text/html; charset=utf-8` |
| ボディ | `templates/index.html` のレンダリング結果 |

**例**

```http
GET / HTTP/1.1
Host: localhost:5000
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html lang="ja">
...
</html>
```

**エラーレスポンス**

| ステータスコード | 発生条件 |
|---|---|
| `405 Method Not Allowed` | `GET` 以外のメソッドでアクセスした場合 |
| `404 Not Found` | 存在しないパスへのアクセス |

---

## 未実装エンドポイント（予定）

以下のエンドポイントは `architecture.md` / `features.md` で設計されているが、**現在は未実装**。

### `POST /api/session`（未実装）

セッション完了をサーバーに記録する。

**リクエスト**

```json
{ "type": "pomodoro" }
```

`type` の取りうる値: `"pomodoro"` / `"short_break"` / `"long_break"`

**レスポンス（予定）**

```json
{ "today_count": 4, "today_focus_minutes": 100 }
```

---

### `GET /api/stats`（未実装）

本日の統計データを返す。

**レスポンス（予定）**

```json
{ "today_count": 4, "today_focus_minutes": 100, "total_count": 42 }
```
