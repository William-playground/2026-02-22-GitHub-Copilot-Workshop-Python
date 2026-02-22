# Pomodoro Timer App
import os
from flask import Flask, render_template, jsonify


def create_app(config=None):
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-only')

    if config:
        app.config.update(config)

    @app.route('/')
    def index():
        """ポモドーロタイマーのメインページ"""
        return render_template('index.html')

    @app.route('/api/settings')
    def settings():
        """タイマー設定を返すAPIエンドポイント"""
        return jsonify({
            'work_minutes': 25,
            'short_break_minutes': 5,
            'long_break_minutes': 15,
        })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')
