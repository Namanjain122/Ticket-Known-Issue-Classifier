# from flask import Flask
# from flask_cors import CORS
# from .routes.api import api_bp
# from .routes.views import views_bp
# from .utils.config import config

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(config)
    
#     # Enable CORS
#     CORS(app)
    
#     # Register blueprints
#     app.register_blueprint(api_bp, url_prefix='/api')
#     app.register_blueprint(views_bp)
    
#     return app

from flask import Flask
from flask_cors import CORS
from app.routes.api import api_bp
from app.routes.views import views_bp
from app.utils.config import config
from app.utils.loggin_config import setup_logging  
import logging

# Setup logging once at import (avoid re-initialization inside create_app)
setup_logging()
logger = logging.getLogger(__name__)

def create_app():
    """
    Flask app factory function.
    Sets up app config, logging, CORS, and blueprints.
    """
    logger.info("🚀 Starting Flask application...")

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)

    # Enable CORS
    CORS(app)
    logger.debug("CORS enabled for the app.")

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(views_bp)
    logger.debug("Blueprints registered: api_bp, views_bp")

    # Log basic app info
    logger.info(
        f"✅ Flask app created with config: DEBUG={app.config.get('DEBUG', False)} | "
        f"DB_SERVER={config.DB_SERVER} | DB_NAME={config.DB_NAME}"
    )

    return app
