"""ルートの統合テスト"""
import json

import pytest


class TestIndexRoute:
    """メインページのテスト"""

    def test_index_returns_200(self, client):
        """メインページが200を返す"""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_timer(self, client):
        """メインページにタイマー要素が含まれる"""
        response = client.get("/")
        assert b"timer-display" in response.data


class TestCompleteSessionRoute:
    """ポモドーロ完了APIのテスト"""

    def test_complete_returns_success(self, client):
        """完了APIが成功レスポンスを返す"""
        response = client.post(
            "/api/pomodoro/complete",
            data=json.dumps({"duration_minutes": 25}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_complete_increases_total_sessions(self, client):
        """完了APIで合計セッション数が増加する"""
        client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        response = client.get("/api/stats")
        data = json.loads(response.data)
        assert data["total_sessions"] == 2

    def test_complete_awards_xp(self, client):
        """完了APIでXPが付与される"""
        response = client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        assert data["xp"]["total_xp"] > 0

    def test_complete_awards_first_badge(self, client):
        """初回完了でfirst_stepバッジが付与される"""
        response = client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        new_badge_ids = [b["id"] for b in data["new_badges"] if b]
        assert "first_step" in new_badge_ids

    def test_complete_no_duplicate_badge(self, client):
        """同じバッジは2度付与されない"""
        client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        response = client.post(
            "/api/pomodoro/complete",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = json.loads(response.data)
        new_badge_ids = [b["id"] for b in data["new_badges"] if b]
        assert "first_step" not in new_badge_ids

    def test_complete_without_body(self, client):
        """リクエストボディなしでも正常に処理される"""
        response = client.post("/api/pomodoro/complete")
        assert response.status_code == 200


class TestStatsRoute:
    """統計APIのテスト"""

    def test_stats_returns_expected_keys(self, client):
        """統計APIが必要なキーを返す"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = json.loads(response.data)
        for key in [
            "total_sessions",
            "sessions_this_week",
            "sessions_this_month",
            "streak",
            "xp",
            "badges",
        ]:
            assert key in data, f"キー '{key}' がレスポンスに含まれていない"

    def test_stats_initial_values(self, client):
        """初期状態の統計値が正しい"""
        response = client.get("/api/stats")
        data = json.loads(response.data)
        assert data["total_sessions"] == 0
        assert data["streak"] == 0
        assert data["xp"]["level"] == 1

    def test_stats_badges_contain_all_definitions(self, client):
        """統計APIが全バッジ定義を返す"""
        response = client.get("/api/stats")
        data = json.loads(response.data)
        assert len(data["badges"]) == 6


class TestWeeklyStatsRoute:
    """週間統計APIのテスト"""

    def test_weekly_returns_seven_entries(self, client):
        """週間統計APIが7エントリを返す"""
        response = client.get("/api/stats/weekly")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["weekly"]) == 7

    def test_weekly_has_date_and_count(self, client):
        """週間統計APIのエントリがdate/countキーを持つ"""
        response = client.get("/api/stats/weekly")
        data = json.loads(response.data)
        for entry in data["weekly"]:
            assert "date" in entry
            assert "count" in entry


class TestMonthlyStatsRoute:
    """月間統計APIのテスト"""

    def test_monthly_returns_four_entries(self, client):
        """月間統計APIが4エントリを返す"""
        response = client.get("/api/stats/monthly")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["monthly"]) == 4

    def test_monthly_has_label_and_count(self, client):
        """月間統計APIのエントリがlabel/countキーを持つ"""
        response = client.get("/api/stats/monthly")
        data = json.loads(response.data)
        for entry in data["monthly"]:
            assert "label" in entry
            assert "count" in entry
