"""テストフィクスチャ"""
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション"""
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret",
        "TESTING": True,
    }
    application = create_app(test_config)
    application.config["TESTING"] = True
    yield application


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """テスト用アプリケーションコンテキスト"""
    with app.app_context():
        yield app
