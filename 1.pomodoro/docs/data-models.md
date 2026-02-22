# データモデル仕様

> **実装状況:** 現時点ではデータモデルは未実装。SQLAlchemy は `requirements.txt` に含まれているが、`app.py` での `db.init_app()` 呼び出しや `models/` ディレクトリはまだ存在しない。

---

## 未実装モデル（設計済み）

以下は `architecture.md` / `features.md` で設計されたモデルであり、**現在はコードとして存在しない**。

### `Session` モデル（予定）

`sessions` テーブルにポモドーロセッションの完了記録を保存する。

| カラム | 型 | 説明 |
|---|---|---|
| `id` | Integer (PK, autoincrement) | セッション ID |
| `type` | String | セッション種別（`"pomodoro"` / `"short_break"` / `"long_break"`） |
| `started_at` | DateTime | セッション開始日時 |
| `completed_at` | DateTime | セッション完了日時 |

**実装予定コード（`models/session.py`）**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=False)
```

---

## リポジトリ層（未実装）

`AbstractSessionRepository` 抽象クラスと `SQLiteSessionRepository` 実装クラスが予定されている。

**実装予定のインターフェース（`repositories/session_repository.py`）**

```python
from abc import ABC, abstractmethod

class AbstractSessionRepository(ABC):
    @abstractmethod
    def save(self, session_type: str) -> None: ...

    @abstractmethod
    def count_today(self) -> int: ...

    @abstractmethod
    def get_today_focus_minutes(self) -> int: ...

    @abstractmethod
    def count_total(self) -> int: ...
```

---

## データベース設定

| 設定キー | デフォルト値 | 説明 |
|---|---|---|
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///pomodoro.db` | DB 接続 URI（環境変数 `DATABASE_URL` で上書き可） |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | 変更追跡の無効化 |

テスト時は `"sqlite:///:memory:"` を使用してインメモリ DB に切り替える（`conftest.py` 参照）。
