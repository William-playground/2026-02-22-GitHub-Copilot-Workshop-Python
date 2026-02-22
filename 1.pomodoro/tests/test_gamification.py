"""ゲーミフィケーションロジックのユニットテスト"""
from datetime import date, timedelta

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gamification


class TestCalculateXp:
    """XP計算のテスト"""

    def test_xp_is_zero_when_no_sessions(self):
        """セッションが0回のときXPは0"""
        assert gamification.calculate_xp(0) == 0

    def test_xp_increases_per_session(self):
        """1セッションごとにXP_PER_SESSION分増加する"""
        assert gamification.calculate_xp(1) == gamification.XP_PER_SESSION
        assert gamification.calculate_xp(4) == 4 * gamification.XP_PER_SESSION

    def test_xp_is_proportional(self):
        """XPはセッション数に比例する"""
        for n in range(1, 10):
            assert gamification.calculate_xp(n) == n * gamification.XP_PER_SESSION


class TestCalculateLevel:
    """レベル計算のテスト"""

    def test_initial_level_is_one(self):
        """XP=0のときレベルは1"""
        assert gamification.calculate_level(0) == 1

    def test_level_increases_with_xp(self):
        """XP_PER_LEVEL到達でレベルが上がる"""
        assert gamification.calculate_level(gamification.XP_PER_LEVEL - 1) == 1
        assert gamification.calculate_level(gamification.XP_PER_LEVEL) == 2
        assert gamification.calculate_level(gamification.XP_PER_LEVEL * 2) == 3

    def test_level_progress_percentage(self):
        """進捗パーセンテージが0〜100の範囲内"""
        for xp in range(0, 500, 10):
            progress = gamification.calculate_xp_progress(xp)
            assert 0 <= progress["percentage"] <= 100


class TestCalculateStreak:
    """ストリーク計算のテスト"""

    def test_empty_streak(self):
        """セッションなしのときストリークは0"""
        assert gamification.calculate_streak([]) == 0

    def test_single_today(self):
        """今日だけのセッションのストリークは1"""
        assert gamification.calculate_streak([date.today()]) == 1

    def test_consecutive_days(self):
        """連続日数が正しくカウントされる"""
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(3)]
        assert gamification.calculate_streak(dates) == 3

    def test_broken_streak(self):
        """途中で途切れたストリークは正しくカウントされる"""
        today = date.today()
        dates = [today, today - timedelta(days=2)]
        assert gamification.calculate_streak(dates) == 1

    def test_old_sessions_no_streak(self):
        """2日以上前のセッションのみの場合ストリークは0"""
        old_date = date.today() - timedelta(days=3)
        assert gamification.calculate_streak([old_date]) == 0

    def test_duplicate_dates_counted_once(self):
        """同日に複数セッションがあっても1日としてカウント"""
        today = date.today()
        dates = [today, today, today - timedelta(days=1)]
        assert gamification.calculate_streak(dates) == 2


class TestCheckNewBadges:
    """バッジ獲得チェックのテスト"""

    def test_first_step_badge(self):
        """初めてのセッションでfirst_stepバッジを獲得"""
        new_badges = gamification.check_new_badges(1, 0, 1, [])
        assert "first_step" in new_badges

    def test_no_duplicate_badges(self):
        """既に獲得済みのバッジは再付与されない"""
        new_badges = gamification.check_new_badges(1, 0, 1, ["first_step"])
        assert "first_step" not in new_badges

    def test_streak_badges(self):
        """ストリーク3日でstreak_3daysバッジを獲得"""
        new_badges = gamification.check_new_badges(3, 3, 3, [])
        assert "streak_3days" in new_badges

    def test_week_badge(self):
        """今週10回完了でten_this_weekバッジを獲得"""
        new_badges = gamification.check_new_badges(10, 1, 10, [])
        assert "ten_this_week" in new_badges

    def test_no_badge_when_condition_not_met(self):
        """条件を満たさない場合はバッジを獲得しない"""
        new_badges = gamification.check_new_badges(0, 0, 0, [])
        assert new_badges == []

    def test_multiple_badges_at_once(self):
        """複数バッジを同時に獲得できる"""
        new_badges = gamification.check_new_badges(5, 3, 5, [])
        assert "five_sessions" in new_badges
        assert "streak_3days" in new_badges


class TestWeeklyStats:
    """週間統計のテスト"""

    def test_returns_seven_days(self):
        """7日分のデータが返る"""
        stats = gamification.get_weekly_stats([])
        assert len(stats) == 7

    def test_today_count(self):
        """今日のセッションが正しくカウントされる"""
        today = date.today()
        stats = gamification.get_weekly_stats([today, today])
        today_entry = next(s for s in stats if s["date"] == today.isoformat())
        assert today_entry["count"] == 2


class TestMonthlyStats:
    """月間統計のテスト"""

    def test_returns_four_weeks(self):
        """4週分のデータが返る"""
        stats = gamification.get_monthly_stats([])
        assert len(stats) == 4

    def test_counts_sessions_in_week(self):
        """今週のセッションが正しくカウントされる"""
        today = date.today()
        stats = gamification.get_monthly_stats([today])
        assert stats[-1]["count"] == 1
