import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET KEY", "dev-only-change-this-before-deployment")
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(
            BASE_DIR, "instance","pathfinder.db"
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False