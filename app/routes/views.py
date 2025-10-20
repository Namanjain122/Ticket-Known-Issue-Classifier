from flask import Blueprint, render_template, jsonify
from app.services.database import db_service
import logging
from datetime import datetime
import os

views_bp = Blueprint('views', __name__)


@views_bp.route("/", methods=["GET"])
def health():
    logging.info("Health check endpoint accessed")
    try:
        # Example: log database connection status
        db_status = "connected" if db_service.is_connected() else "disconnected"
        logging.info(f"Database status: {db_status}")
        
        return jsonify({"status": "ok", "model": "ready", "database": db_status}), 200
    except Exception as e:
        logging.error(f"Error in health endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500