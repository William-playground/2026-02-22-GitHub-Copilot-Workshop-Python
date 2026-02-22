# Pomodoro Timer App
import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()


def create_app(config: dict | None = None) -> Flask:
    """アプリケーションファクトリ。テスト時は config で設定を上書き可能。"""
    app = Flask(__name__)

    # デフォルト設定
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///pomodoro.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # テスト用設定を上書き
    if config:
        app.config.update(config)

    # ルート定義
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
