from flask import Flask

from app.config import config
from app.extensions import setupExtensions


def createApp(configType: str) -> Flask:

    # create application
    app: Flask = Flask(__name__)
    # setup config
    app.config.from_object(config[configType])
    config[configType].init_app(app)
    # install blueprints
    from app.main import main
    app.register_blueprint(main)
    from app.api import api
    app.register_blueprint(api, url_prefix='/api')
    print(app.url_map)
    return app