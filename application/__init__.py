from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def create_app(config_class=Config):
    from application.routes.login import login_bp
    from application.routes.sales import sales_bp
    from application.routes.index import index_bp
    # from application.routes.search import search_bp
    # from application.routes.reports import reports_bp
    # from application.routes.members import members_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(index_bp)
    # app.register_blueprint(search_bp)
    # app.register_blueprint(reports)
    # app.register_blueprint(members)

    return app
