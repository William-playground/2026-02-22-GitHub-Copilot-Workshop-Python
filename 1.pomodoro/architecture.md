# ポモドーロタイマー Webアプリ — アーキテクチャ設計書

## 概要

Flask（バックエンド）と Vanilla HTML/CSS/JavaScript（フロントエンド）を使用したポモドーロタイマー Web アプリケーション。  
タイマーのカウントダウンはフロントエンドが完全に管理し、セッション完了時のみサーバーへ記録を送信するシンプルな構成とする。  
ユニットテストの容易性を考慮し、ビジネスロジック・DB アクセス・Flask ルートを明確に分離したレイヤードアーキテクチャを採用する。

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                        # Flask エントリーポイント（ルート定義のみ）
├── requirements.txt              # 本番依存パッケージ
├── requirements-dev.txt          # 開発・テスト用パッケージ
│
├── models/
│   ├── __init__.py
│   └── session.py                # SQLAlchemy モデル定義
│
├── repositories/
│   ├── __init__.py
│   └── session_repository.py     # DB アクセス層（抽象クラス + SQLite 実装）
│
├── services/
│   ├── __init__.py
│   └── session_service.py        # ビジネスロジック（Flask に非依存）
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest フィクスチャ（テスト用インメモリ DB など）
│   ├── test_session_service.py   # ビジネスロジックの単体テスト
│   ├── test_session_repository.py
│   └── test_routes.py            # Flask ルートの統合テスト
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── timer.js              # タイマーロジック（DOM 非依存クラス）
│   │   └── main.js               # DOM 操作・イベントハンドラ
│   └── audio/
│       └── bell.mp3              # タイマー終了音
│
└── templates/
    └── index.html                # メイン画面（単一ページ）
```

---

## アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (Client)                       │
│                                                             │
│  ┌────────────────┐      ┌──────────────────────────────┐  │
│  │  index.html    │      │  JavaScript                  │  │
│  │  (表示・UI)    │ ←──→ │  timer.js  : タイマー制御     │  │
│  │                │      │  main.js   : DOM 操作         │  │
│  └────────────────┘      └──────────────┬───────────────┘  │
│                                         │ fetch API（完了時のみ）
└─────────────────────────────────────────┼─────────────────────┘
                                          │ HTTP REST
┌─────────────────────────────────────────▼─────────────────────┐
│                        Flask (Server)                         │
│                                                               │
│  app.py（ルート）                                              │
│    GET  /              → index.html を返す                    │
│    POST /api/session   → セッション完了を記録                  │
│    GET  /api/stats     → 統計データを JSON で返す              │
│         ↓ 依存性注入（DI）                                     │
│  services/session_service.py（ビジネスロジック）               │
│         ↓ 抽象インターフェースに依存                           │
│  repositories/session_repository.py（DB アクセス層）          │
│         ↓                                                     │
│  SQLite（sessions テーブル）                                   │
│    id / type / started_at / completed_at                      │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│               tests/（pytest / Jest）                         │
│  ・session_service → Fake リポジトリで Flask 不要の単体テスト  │
│  ・session_repository → インメモリ SQLite で DB テスト         │
│  ・routes → Flask テストクライアントで統合テスト               │
│  ・timer.js → PomodoroTimer クラスを Jest で単体テスト         │
└───────────────────────────────────────────────────────────────┘
```

---

## 各コンポーネントの役割

| コンポーネント | 技術 | 役割 |
|---|---|---|
| **Flask (`app.py`)** | Python / Flask | HTML 配信・REST API（ルート定義のみ、薄く保つ） |
| **SessionService** | Python | セッション完了処理・統計集計ロジック |
| **AbstractSessionRepository** | Python (ABC) | DB アクセスの抽象インターフェース |
| **SQLiteSessionRepository** | Python / SQLAlchemy | SQLite への CRUD 実装 |
| **PomodoroTimer クラス** | JavaScript | タイマー制御ロジック（DOM 非依存） |
| **main.js** | JavaScript | DOM 操作・API 呼び出し・イベント管理 |
| **SQLite** | SQLite | セッション記録の永続化 |

---

## タイマーモード

| モード | デフォルト時間 |
|---|---|
| ポモドーロ | 25 分 |
| 短い休憩 | 5 分 |
| 長い休憩 | 15 分 |

---

## REST API 設計

| エンドポイント | メソッド | リクエスト | レスポンス |
|---|---|---|---|
| `/` | GET | — | `index.html` |
| `/api/session` | POST | `{ "type": "pomodoro" }` | `{ "today_count": 3 }` |
| `/api/stats` | GET | — | `{ "today": 3, "total": 42 }` |

---

## JavaScript タイマー状態管理

```
タイマー状態:
  - mode         : "pomodoro" | "short_break" | "long_break"
  - status       : "idle" | "running" | "paused"
  - remainingSeconds : number
  - pomodoroCount    : number（連続完了数、4回で長い休憩を提案）
```

タイマーの tick は `setInterval`（1 秒間隔）でフロントエンドが完全に管理する。  
**サーバーへのリクエストはセッション完了時のみ**（統計保存 POST）。

---

## テスト戦略

### Python バックエンド（pytest）

```python
# repositories/session_repository.py
class AbstractSessionRepository(ABC):
    @abstractmethod
    def save(self, session_type: str) -> None: ...
    @abstractmethod
    def count_today(self) -> int: ...

class SQLiteSessionRepository(AbstractSessionRepository): ...

# テスト用フェイク（DB 不要）
class FakeSessionRepository(AbstractSessionRepository):
    def __init__(self): self.sessions = []
    def save(self, session_type): self.sessions.append(session_type)
    def count_today(self): return len(self.sessions)
```

```python
# services/session_service.py（DI パターン）
class SessionService:
    def __init__(self, repo: AbstractSessionRepository):
        self.repo = repo

    def complete_session(self, session_type: str) -> dict:
        self.repo.save(session_type)
        return {"today_count": self.repo.count_today()}
```

```python
# app.py（アプリファクトリパターン）
def create_app(config: dict | None = None):
    app = Flask(__name__)
    if config:
        app.config.update(config)
    return app
```

```python
# tests/conftest.py
@pytest.fixture
def app():
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
```

### JavaScript フロントエンド（Jest）

```javascript
// static/js/timer.js（DOM 非依存クラス）
export class PomodoroTimer {
    constructor(onTick, onComplete) { ... }
    start(durationSeconds) { ... }
    pause() { ... }
    reset() { ... }
}

// static/js/main.js（DOM 操作はここに集約）
import { PomodoroTimer } from './timer.js';
```

---

## 技術スタック

### 本番（`requirements.txt`）

```
Flask>=3.0
Flask-SQLAlchemy
python-dotenv
```

### 開発・テスト（`requirements-dev.txt`）

```
pytest
pytest-cov
pytest-flask
```
