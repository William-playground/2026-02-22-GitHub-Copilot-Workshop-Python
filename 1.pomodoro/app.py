"""ポモドーロタイマー Flask アプリケーション"""
from flask import Flask, render_template, request, jsonify, session
import secrets


def create_app(config=None):
    """Flask application factory"""
    app = Flask(__name__)
    
    # デフォルト設定
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # カスタム設定を適用
    if config:
        app.config.update(config)
    
    # デフォルトのポモドーロ設定
    DEFAULT_SETTINGS = {
        "work_minutes": 25,
        "break_minutes": 5,
        "theme": "dark",
        "sound_start": True,
        "sound_end": True,
        "sound_tick": False
    }
    
    @app.route('/')
    def index():
        """メインページ"""
        # セッションにデフォルト設定がなければ初期化
        if 'settings' not in session:
            session['settings'] = DEFAULT_SETTINGS.copy()
        return render_template('index.html')
    
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        """現在の設定を取得"""
        if 'settings' not in session:
            session['settings'] = DEFAULT_SETTINGS.copy()
        return jsonify(session['settings'])
    
    @app.route('/api/settings', methods=['POST'])
    def update_settings():
        """設定を更新"""
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # 現在の設定を取得（存在しなければデフォルト）
        if 'settings' not in session:
            session['settings'] = DEFAULT_SETTINGS.copy()
        
        current_settings = session['settings']
        
        # バリデーション
        if 'work_minutes' in data:
            if data['work_minutes'] not in [15, 25, 35, 45]:
                return jsonify({"error": "Invalid work_minutes"}), 400
            current_settings['work_minutes'] = data['work_minutes']
        
        if 'break_minutes' in data:
            if data['break_minutes'] not in [5, 10, 15]:
                return jsonify({"error": "Invalid break_minutes"}), 400
            current_settings['break_minutes'] = data['break_minutes']
        
        if 'theme' in data:
            if data['theme'] not in ['dark', 'light', 'focus']:
                return jsonify({"error": "Invalid theme"}), 400
            current_settings['theme'] = data['theme']
        
        if 'sound_start' in data:
            if not isinstance(data['sound_start'], bool):
                return jsonify({"error": "Invalid sound_start"}), 400
            current_settings['sound_start'] = data['sound_start']
        
        if 'sound_end' in data:
            if not isinstance(data['sound_end'], bool):
                return jsonify({"error": "Invalid sound_end"}), 400
            current_settings['sound_end'] = data['sound_end']
        
        if 'sound_tick' in data:
            if not isinstance(data['sound_tick'], bool):
                return jsonify({"error": "Invalid sound_tick"}), 400
            current_settings['sound_tick'] = data['sound_tick']
        
        # セッションに保存
        session['settings'] = current_settings
        session.modified = True
        
        return jsonify(current_settings)
    
    return app


if __name__ == '__main__':
    import os
    app = create_app()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
