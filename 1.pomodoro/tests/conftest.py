"""pytest設定ファイル"""
import pytest
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションインスタンスを作成"""
    app = create_app({'TESTING': True})
    yield app


@pytest.fixture
def client(app):
    """テスト用のFlaskクライアントを作成"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テスト用のCLIランナーを作成"""
    return app.test_cli_runner()
