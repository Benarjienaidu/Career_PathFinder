
from datetime import datetime, timezone

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Existing assessment fields
    education = db.Column(db.String(50), nullable=False)
    interest = db.Column(db.String(50), nullable=False)

    # These are placeholders until Step 2 measures actual ability.
    python_level = db.Column(db.Integer, nullable=False, default=0)
    math_level = db.Column(db.Integer, nullable=False, default=0)
    coding_level = db.Column(db.Integer, nullable=False, default=0)

    daily_hours = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(50), nullable=False)

    # New Step 1: Discovery answers
    situation = db.Column(db.String(50), nullable=True)
    favorite_subject = db.Column(db.String(50), nullable=True)
    work_style = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    dislike = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship("User", backref="assessments")

    def __repr__(self):
        return f"<Assessment {self.id} for user {self.user_id}>"
