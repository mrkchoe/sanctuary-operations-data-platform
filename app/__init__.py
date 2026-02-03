from flask import Flask, redirect, url_for
from flask_login import login_required

from app.config import Config
from app.extensions import csrf, db, login_manager


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.auth.routes import auth_bp
    from app.dogs.routes import dogs_bp
    from app.care.routes import care_bp
    from app.adoptions.routes import adoptions_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dogs_bp)
    app.register_blueprint(care_bp)
    app.register_blueprint(adoptions_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("dogs.list_dogs"))

    return app
