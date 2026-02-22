"""ポモドーロタイマーのゲーミフィケーションロジック"""
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

XP_PER_SESSION = 25
XP_PER_LEVEL = 100

BADGE_DEFINITIONS: List[Dict[str, str]] = [
    {
        "id": "first_step",
        "name": "初めての一歩",
        "description": "初めてのポモドーロを完了しました",
        "icon": "🌱",
    },
    {
        "id": "five_sessions",
        "name": "集中の芽生え",
        "description": "合計5回のポモドーロを完了しました",
        "icon": "🌿",
    },
    {
        "id": "streak_3days",
        "name": "3日連続",
        "description": "3日間連続でポモドーロを完了しました",
        "icon": "🔥",
    },
    {
        "id": "streak_7days",
        "name": "週間ストリーク",
        "description": "7日間連続でポモドーロを完了しました",
        "icon": "⚡",
    },
    {
        "id": "ten_this_week",
        "name": "今週10回",
        "description": "今週10回のポモドーロを完了しました",
        "icon": "🏆",
    },
    {
        "id": "twenty_five_total",
        "name": "ポモドーロマスター",
        "description": "合計25回のポモドーロを完了しました",
        "icon": "👑",
    },
]


def calculate_xp(total_sessions: int) -> int:
    """セッション数からXPを計算する"""
    return total_sessions * XP_PER_SESSION


def calculate_level(total_xp: int) -> int:
    """XPからレベルを計算する"""
    return (total_xp // XP_PER_LEVEL) + 1


def calculate_xp_progress(total_xp: int) -> Dict[str, int]:
    """現在のレベル内XP進捗情報を返す"""
    level = calculate_level(total_xp)
    xp_for_current_level = (level - 1) * XP_PER_LEVEL
    xp_for_next_level = level * XP_PER_LEVEL
    xp_progress = total_xp - xp_for_current_level
    xp_needed = xp_for_next_level - xp_for_current_level
    percentage = int(xp_progress / xp_needed * 100) if xp_needed > 0 else 0
    return {
        "level": level,
        "total_xp": total_xp,
        "xp_progress": xp_progress,
        "xp_needed": xp_needed,
        "percentage": percentage,
    }


def calculate_streak(session_dates: List[date]) -> int:
    """連続日数（ストリーク）を計算する"""
    if not session_dates:
        return 0
    unique_dates = sorted(set(session_dates), reverse=True)
    today = date.today()
    if unique_dates[0] < today - timedelta(days=1):
        return 0
    streak = 1
    for i in range(1, len(unique_dates)):
        if unique_dates[i] == unique_dates[i - 1] - timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def get_sessions_this_week(session_dates: List[date]) -> List[date]:
    """今週のセッション日付リストを返す（月曜始まり）"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    return [d for d in session_dates if d >= week_start]


def get_sessions_this_month(session_dates: List[date]) -> List[date]:
    """今月のセッション日付リストを返す"""
    today = date.today()
    return [
        d for d in session_dates if d.year == today.year and d.month == today.month
    ]


def check_new_badges(
    total_sessions: int,
    streak: int,
    sessions_this_week: int,
    earned_badge_ids: List[str],
) -> List[str]:
    """新たに獲得したバッジのIDリストを返す"""
    conditions: Dict[str, bool] = {
        "first_step": total_sessions >= 1,
        "five_sessions": total_sessions >= 5,
        "streak_3days": streak >= 3,
        "streak_7days": streak >= 7,
        "ten_this_week": sessions_this_week >= 10,
        "twenty_five_total": total_sessions >= 25,
    }
    return [
        badge_id
        for badge_id, met in conditions.items()
        if met and badge_id not in earned_badge_ids
    ]


def get_badge_info(badge_id: str) -> Optional[Dict[str, str]]:
    """バッジIDからバッジ情報を取得する"""
    for badge in BADGE_DEFINITIONS:
        if badge["id"] == badge_id:
            return badge
    return None


def get_weekly_stats(session_dates: List[date]) -> List[Dict[str, Any]]:
    """過去7日間の日別セッション数を返す"""
    today = date.today()
    stats = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = sum(1 for d in session_dates if d == day)
        stats.append({"date": day.isoformat(), "count": count})
    return stats


def get_monthly_stats(session_dates: List[date]) -> List[Dict[str, Any]]:
    """過去4週間の週別セッション数を返す"""
    today = date.today()
    stats = []
    for i in range(3, -1, -1):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        count = sum(1 for d in session_dates if week_start <= d <= week_end)
        label = f"{week_start.month}/{week_start.day}〜{week_end.month}/{week_end.day}"
        stats.append({"label": label, "count": count})
    return stats
