"""pytest 共通フィクスチャ"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """テスト用 Flask アプリケーション。インメモリ SQLite を使用する。"""
    return create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
        }
    )


@pytest.fixture
def client(app):
    """テスト用 HTTP クライアント。"""
    return app.test_client()


@pytest.fixture
def app_ctx(app):
    """アプリケーションコンテキストを提供する。"""
    with app.app_context():
        yield app
