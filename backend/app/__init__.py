from flask import Flask
from .database import init_db

#this Initiliazzed Our Flask applicaton 

def create_app(test_config=None):
    #Config for ou FrontEnd Asets
    app = Flask(
        __name__,
        static_folder="../../frontend",
        static_url_path=""
    )
     
    #Config for Our UserName + Password
    app.config.from_mapping(
        DB_NAME="tasks.db",
        SECRET_KEY="dev-secret-key",
        TESTING=False
    )

    if test_config:
        app.config.update(test_config)
     
    from .routes import api, auth
    app.register_blueprint(api)
    app.register_blueprint(auth)

    with app.app_context():
        init_db()

    return app