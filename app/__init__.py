import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("app.config.Config")

    # Ensure instance folder exists (for SQLite file)
    os.makedirs(app.config["INSTANCE_DIR"], exist_ok=True)

    db.init_app(app)

    # Register only the main blueprint for now
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    # Create DB file + tables (even if models empty, DB file gets created on first run)
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app

