from flask import Flask
from .database import init_db


# Purpose:
# Initializes the Flask application and configures the app


def create_app(test_config=None):
    # -----------------------------
    # Create Flask App
    # -----------------------------
    app = Flask(
        __name__,
        static_folder="../../frontend",
        static_url_path=""
    )

    # -----------------------------
    # Default Configuration
    # -----------------------------
    app.config.from_mapping(
        DB_NAME="tasks.db",
        SECRET_KEY="dev-secret-key",  # change for production
        TESTING=False
    )

    # Allow overrides (used in testing)
    if test_config:
        app.config.update(test_config)

    # -----------------------------
    # Register Blueprints
    # -----------------------------
    from .routes import api, auth
    app.register_blueprint(api)
    app.register_blueprint(auth)

    # -----------------------------
    # Initialize Database
    # -----------------------------
    with app.app_context():
        init_db()

    return app