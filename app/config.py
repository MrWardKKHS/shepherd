import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    # SQLite in /instance (created if missing)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    DB_PATH = os.path.join(INSTANCE_DIR, "shepherd.sqlite3")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False
