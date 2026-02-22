"""ルートのテスト"""
import json


class TestIndex:
    """メインページのテスト"""
    
    def test_index_returns_200(self, client):
        """GET / が200を返すことを確認"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'pomodoro' in response.data.lower() or 'ポモドーロ'.encode('utf-8') in response.data


class TestSettings:
    """設定APIのテスト"""
    
    def test_get_settings_returns_default(self, client):
        """GET /api/settings がデフォルト設定を返すことを確認"""
        response = client.get('/api/settings')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['work_minutes'] == 25
        assert data['break_minutes'] == 5
        assert data['theme'] == 'dark'
        assert data['sound_start'] is True
        assert data['sound_end'] is True
        assert data['sound_tick'] is False
    
    def test_post_settings_updates_work_minutes(self, client):
        """POST /api/settings で作業時間を更新できることを確認"""
        new_settings = {'work_minutes': 35}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['work_minutes'] == 35
    
    def test_post_settings_updates_break_minutes(self, client):
        """POST /api/settings で休憩時間を更新できることを確認"""
        new_settings = {'break_minutes': 10}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['break_minutes'] == 10
    
    def test_post_settings_updates_theme(self, client):
        """POST /api/settings でテーマを更新できることを確認"""
        new_settings = {'theme': 'light'}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['theme'] == 'light'
    
    def test_post_settings_updates_sound_settings(self, client):
        """POST /api/settings でサウンド設定を更新できることを確認"""
        new_settings = {
            'sound_start': False,
            'sound_end': False,
            'sound_tick': True
        }
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['sound_start'] is False
        assert data['sound_end'] is False
        assert data['sound_tick'] is True
    
    def test_post_settings_rejects_invalid_work_minutes(self, client):
        """POST /api/settings が不正な作業時間を拒否することを確認"""
        new_settings = {'work_minutes': 99}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_settings_rejects_invalid_break_minutes(self, client):
        """POST /api/settings が不正な休憩時間を拒否することを確認"""
        new_settings = {'break_minutes': 20}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_settings_rejects_invalid_theme(self, client):
        """POST /api/settings が不正なテーマを拒否することを確認"""
        new_settings = {'theme': 'rainbow'}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_settings_rejects_invalid_sound_start(self, client):
        """POST /api/settings が不正な開始音設定を拒否することを確認"""
        new_settings = {'sound_start': 'yes'}
        response = client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_settings_rejects_invalid_json(self, client):
        """POST /api/settings が不正なJSONを拒否することを確認"""
        response = client.post(
            '/api/settings',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_settings_persistence_in_session(self, client):
        """設定がセッションに保存されることを確認"""
        # 設定を更新
        new_settings = {'work_minutes': 45, 'theme': 'focus'}
        client.post(
            '/api/settings',
            data=json.dumps(new_settings),
            content_type='application/json'
        )
        
        # 設定を再取得して確認
        response = client.get('/api/settings')
        data = json.loads(response.data)
        assert data['work_minutes'] == 45
        assert data['theme'] == 'focus'
