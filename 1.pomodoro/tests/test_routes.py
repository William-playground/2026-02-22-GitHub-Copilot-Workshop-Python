"""ポモドーロタイマー ルートテスト"""
import pytest
import json


class TestIndexRoute:
    """メインページ (/) のテスト"""

    def test_index_returns_200(self, client):
        """インデックスページが200を返すこと"""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_contains_timer_elements(self, client):
        """インデックスページに必要なUI要素が含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'progressCircle' in html
        assert 'timeDisplay' in html
        assert 'particleCanvas' in html
        assert 'rippleOverlay' in html

    def test_index_loads_css(self, client):
        """インデックスページがCSSを読み込むこと"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'style.css' in html

    def test_index_loads_js(self, client):
        """インデックスページがJavaScriptを読み込むこと"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'timer.js' in html

    def test_index_contains_mode_buttons(self, client):
        """インデックスページにモード切替ボタンが含まれること"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'mode-btn' in html
        assert '集中' in html
        assert '短休憩' in html
        assert '長休憩' in html


class TestSettingsRoute:
    """設定API (/api/settings) のテスト"""

    def test_settings_returns_200(self, client):
        """/api/settings が200を返すこと"""
        response = client.get('/api/settings')
        assert response.status_code == 200

    def test_settings_returns_json(self, client):
        """/api/settings がJSONを返すこと"""
        response = client.get('/api/settings')
        assert response.content_type == 'application/json'

    def test_settings_work_minutes(self, client):
        """集中時間が25分であること"""
        response = client.get('/api/settings')
        data = json.loads(response.data)
        assert data['work_minutes'] == 25

    def test_settings_short_break_minutes(self, client):
        """短休憩が5分であること"""
        response = client.get('/api/settings')
        data = json.loads(response.data)
        assert data['short_break_minutes'] == 5

    def test_settings_long_break_minutes(self, client):
        """長休憩が15分であること"""
        response = client.get('/api/settings')
        data = json.loads(response.data)
        assert data['long_break_minutes'] == 15


class TestStaticFiles:
    """静的ファイルのテスト"""

    def test_css_file_accessible(self, client):
        """CSSファイルが取得できること"""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200

    def test_js_file_accessible(self, client):
        """JSファイルが取得できること"""
        response = client.get('/static/js/timer.js')
        assert response.status_code == 200

    def test_css_contains_progress_animation(self, client):
        """CSSに円形プログレスバーのスタイルが含まれること"""
        response = client.get('/static/css/style.css')
        css = response.data.decode('utf-8')
        assert 'progress-ring' in css
        assert 'stroke-dashoffset' in css

    def test_css_contains_particle_canvas(self, client):
        """CSSにパーティクルキャンバスのスタイルが含まれること"""
        response = client.get('/static/css/style.css')
        css = response.data.decode('utf-8')
        assert 'particleCanvas' in css

    def test_css_contains_ripple_animation(self, client):
        """CSSに波紋アニメーションが含まれること"""
        response = client.get('/static/css/style.css')
        css = response.data.decode('utf-8')
        assert 'rippleAnim' in css

    def test_js_contains_color_transition(self, client):
        """JSに色変化ロジックが含まれること"""
        response = client.get('/static/js/timer.js')
        js = response.data.decode('utf-8')
        assert 'COLOR_BLUE' in js
        assert 'COLOR_YELLOW' in js
        assert 'COLOR_RED' in js
        assert 'getProgressColor' in js

    def test_js_contains_particle_effect(self, client):
        """JSにパーティクルエフェクトが含まれること"""
        response = client.get('/static/js/timer.js')
        js = response.data.decode('utf-8')
        assert 'Particle' in js
        assert 'animateParticles' in js

    def test_js_contains_ripple_effect(self, client):
        """JSに波紋エフェクトが含まれること"""
        response = client.get('/static/js/timer.js')
        js = response.data.decode('utf-8')
        assert 'triggerRipple' in js
