# アーキテクチャ概要

> **実装状況:** 現時点では Step 1（プロジェクト骨格）のみ完了。Flask の起動と `GET /` によるHTML配信が動作する状態。

---

## 現在の構成

```
1.pomodoro/
├── app.py                  # Flask エントリーポイント（create_app() ファクトリ）
├── requirements.txt        # 本番依存パッケージ
├── requirements-dev.txt    # 開発・テスト用パッケージ
├── templates/
│   └── index.html          # メイン画面（プレースホルダー）
└── tests/
    ├── __init__.py
    ├── conftest.py         # pytest フィクスチャ
    └── test_routes.py      # GET / および create_app() のテスト
```

### 未実装（設計済み・今後追加予定）

```
├── models/                 # SQLAlchemy モデル
├── repositories/           # DB アクセス層
├── services/               # ビジネスロジック
├── static/
│   ├── css/style.css
│   ├── js/timer.js
│   └── js/main.js
└── tests/
    ├── test_session_service.py
    └── test_session_repository.py
```

---

## レイヤー構成（現在）

```
Browser
  └── GET /  →  Flask (app.py)  →  templates/index.html
```

Flask アプリは `create_app()` ファクトリパターンで生成される。現在定義されているルートは `GET /` のみ。

---

## アプリケーションファクトリ (`app.py`)

```python
def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///pomodoro.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
```

- `config` 引数でテスト時の設定上書きが可能（`TESTING: True`、インメモリ SQLite など）
- 環境変数は `python-dotenv` の `load_dotenv()` でロードされる

---

## 技術スタック

### 本番 (`requirements.txt`)

| パッケージ | バージョン | 用途 |
|---|---|---|
| Flask | `>=3.0` | Web フレームワーク |
| Flask-SQLAlchemy | `>=3.0` | ORM（未使用、将来の DB 連携用） |
| python-dotenv | `>=1.0` | 環境変数管理 |

### 開発・テスト (`requirements-dev.txt`)

| パッケージ | バージョン | 用途 |
|---|---|---|
| pytest | `>=8.0` | テストフレームワーク |
| pytest-cov | `>=5.0` | カバレッジ計測 |
| pytest-flask | `>=1.3` | Flask テストユーティリティ |

---

## テスト構成

`tests/conftest.py` でテスト用フィクスチャを定義。

```python
@pytest.fixture
def app():
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
    })

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield app
```

現在のテスト対象:

- `GET /` のステータスコード・Content-Type・HTML 内容
- `create_app()` のデフォルト設定・設定上書き動作
- URL ルーティング（`/` の存在確認、未知パスの 404）

---

## 設計目標（将来の完成形）

設計の詳細は [`../architecture.md`](../architecture.md) を参照。  
実装予定の機能一覧は [`../features.md`](../features.md) を参照。  
実装手順は [`../plan.md`](../plan.md) を参照。
