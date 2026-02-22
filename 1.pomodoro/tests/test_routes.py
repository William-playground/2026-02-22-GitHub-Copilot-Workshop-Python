"""GET / ルートのテスト"""


class TestIndexRoute:
    """GET / のテストスイート"""

    def test_returns_200(self, client):
        """GET / は HTTP 200 を返すこと"""
        response = client.get("/")
        assert response.status_code == 200

    def test_returns_html_content_type(self, client):
        """GET / は Content-Type: text/html を返すこと"""
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_contains_title(self, client):
        """レスポンス HTML にアプリ名が含まれること"""
        response = client.get("/")
        assert "ポモドーロタイマー" in response.data.decode("utf-8")

    def test_post_method_not_allowed(self, client):
        """GET / に POST リクエストすると 405 を返すこと"""
        response = client.post("/")
        assert response.status_code == 405

    def test_unknown_route_returns_404(self, client):
        """存在しないパスへのアクセスは 404 を返すこと"""
        response = client.get("/not-exist")
        assert response.status_code == 404


class TestCreateApp:
    """create_app() ファクトリ関数のテストスイート"""

    def test_default_config_is_applied(self, app):
        """デフォルト設定が正しく適用されること"""
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

    def test_testing_flag_is_set(self, app):
        """TESTING フラグが有効になっていること"""
        assert app.config["TESTING"] is True

    def test_custom_config_overrides_default(self):
        """カスタム設定でデフォルトを上書きできること"""
        from app import create_app

        custom_app = create_app({"SECRET_KEY": "custom-key"})
        assert custom_app.config["SECRET_KEY"] == "custom-key"

    def test_database_url_can_be_overridden(self):
        """DATABASE_URL をテスト用インメモリ SQLite に上書きできること"""
        from app import create_app

        custom_app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        assert custom_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"

    def test_app_has_index_route(self, app):
        """アプリに / ルートが登録されていること"""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert "/" in rules
