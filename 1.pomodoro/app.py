# Pomodoro Timer App
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

import gamification

db = SQLAlchemy()


class PomodoroSession(db.Model):
    """ポモドーロセッションモデル"""

    id = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    duration_minutes = db.Column(db.Integer, nullable=False, default=25)


class EarnedBadge(db.Model):
    """獲得済みバッジモデル"""

    id = db.Column(db.Integer, primary_key=True)
    badge_id = db.Column(db.String(64), nullable=False, unique=True)
    earned_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


def create_app(config=None):
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__)

    if config is None:
        config = {}

    app.config["SQLALCHEMY_DATABASE_URI"] = config.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///pomodoro.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = config.get("SECRET_KEY", "dev-secret-key")

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        """メインページ"""
        return render_template("index.html")

    @app.route("/api/pomodoro/complete", methods=["POST"])
    def complete_session():
        """ポモドーロセッション完了API"""
        data = request.get_json(silent=True) or {}
        duration = int(data.get("duration_minutes", 25))

        session = PomodoroSession(
            completed_at=datetime.now(timezone.utc), duration_minutes=duration
        )
        db.session.add(session)
        db.session.flush()

        all_sessions = PomodoroSession.query.all()
        total_sessions = len(all_sessions)
        session_dates = [s.completed_at.date() for s in all_sessions]

        streak = gamification.calculate_streak(session_dates)
        this_week_dates = gamification.get_sessions_this_week(session_dates)
        sessions_this_week = len(this_week_dates)

        earned_badge_ids = [b.badge_id for b in EarnedBadge.query.all()]
        new_badge_ids = gamification.check_new_badges(
            total_sessions, streak, sessions_this_week, earned_badge_ids
        )

        for badge_id in new_badge_ids:
            db.session.add(EarnedBadge(badge_id=badge_id))

        db.session.commit()

        total_xp = gamification.calculate_xp(total_sessions)
        xp_progress = gamification.calculate_xp_progress(total_xp)
        new_badges_info = [
            gamification.get_badge_info(bid) for bid in new_badge_ids
        ]

        return jsonify(
            {
                "success": True,
                "total_sessions": total_sessions,
                "xp": xp_progress,
                "streak": streak,
                "new_badges": new_badges_info,
            }
        )

    @app.route("/api/stats")
    def get_stats():
        """統計情報取得API"""
        all_sessions = PomodoroSession.query.all()
        total_sessions = len(all_sessions)
        session_dates = [s.completed_at.date() for s in all_sessions]

        streak = gamification.calculate_streak(session_dates)
        this_week_dates = gamification.get_sessions_this_week(session_dates)
        this_month_dates = gamification.get_sessions_this_month(session_dates)

        total_xp = gamification.calculate_xp(total_sessions)
        xp_progress = gamification.calculate_xp_progress(total_xp)

        earned_badges = EarnedBadge.query.order_by(EarnedBadge.earned_at).all()
        badges_info = []
        for badge in gamification.BADGE_DEFINITIONS:
            earned = next(
                (b for b in earned_badges if b.badge_id == badge["id"]), None
            )
            badges_info.append(
                {
                    **badge,
                    "earned": earned is not None,
                    "earned_at": earned.earned_at.isoformat() if earned else None,
                }
            )

        return jsonify(
            {
                "total_sessions": total_sessions,
                "sessions_this_week": len(this_week_dates),
                "sessions_this_month": len(this_month_dates),
                "streak": streak,
                "xp": xp_progress,
                "badges": badges_info,
            }
        )

    @app.route("/api/stats/weekly")
    def get_weekly_stats():
        """週間統計取得API"""
        all_sessions = PomodoroSession.query.all()
        session_dates = [s.completed_at.date() for s in all_sessions]
        stats = gamification.get_weekly_stats(session_dates)
        return jsonify({"weekly": stats})

    @app.route("/api/stats/monthly")
    def get_monthly_stats():
        """月間統計取得API"""
        all_sessions = PomodoroSession.query.all()
        session_dates = [s.completed_at.date() for s in all_sessions]
        stats = gamification.get_monthly_stats(session_dates)
        return jsonify({"monthly": stats})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
