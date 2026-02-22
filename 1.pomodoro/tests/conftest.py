"""pytest 共通フィクスチャ"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """テスト用Flaskアプリケーションを生成する"""
    application = create_app({'TESTING': True})
    return application


@pytest.fixture
def client(app):
    """テスト用HTTPクライアントを生成する"""
    return app.test_client()
