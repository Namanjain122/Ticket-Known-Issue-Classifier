# from flask import Blueprint, jsonify, request
# import pandas as pd
# import os
# from app.services.database import db_service
# from app.services.similarity_service import similarity_service
# from app.utils.config import config
# import torch
# import logging
# from datetime import datetime
# import threading
# import time
# from datetime import timedelta

# api_bp = Blueprint('api', __name__)

# # Configure logging
# def setup_api_logging():
#     """Setup logging for API endpoints"""
#     log_dir = 'logs/api'
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)
    
#     # API-specific logger
#     logger = logging.getLogger('api')
#     logger.setLevel(logging.INFO)
    
#     # Remove any existing handlers to avoid duplicates
#     if logger.handlers:
#         logger.handlers.clear()
    
#     # File handler
#     file_handler = logging.FileHandler(
#         f'{log_dir}/api_{datetime.now().strftime("%Y%m%d")}.log',
#         encoding='utf-8'
#     )
#     file_handler.setLevel(logging.INFO)
    
#     # Formatter
#     formatter = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
#     )
#     file_handler.setFormatter(formatter)
    
#     logger.addHandler(file_handler)
#     logger.propagate = False  # Prevent duplication with root logger
    
#     return logger

# # Create API logger
# api_logger = setup_api_logging()

# # Global variables for caching
# predefined_issues = []
# predefined_embeddings = None
# last_refresh_time = None
# refresh_interval_hours = 24 
# refresh_lock = threading.Lock()  # Add a lock for thread safety

# def load_issues_from_db():
#     """Load issues from database and update embeddings - thread safe"""
#     global predefined_issues, predefined_embeddings, last_refresh_time
    
#     with refresh_lock:  # Ensure thread safety
#         try:
#             api_logger.info("Loading predefined issues from database")
#             new_issues = db_service.get_known_issues()
            
#             if not new_issues:
#                 api_logger.warning("No predefined issues found in database")
#                 return False
            
#             predefined_issues = new_issues
#             predefined_names = [issue[1] for issue in predefined_issues]
#             api_logger.info(f"Loaded {len(predefined_issues)} issues from database")
            
#             similarity_service.update_embeddings(predefined_names)
#             predefined_embeddings = torch.stack(
#                 [similarity_service.issue_embeddings_cache[name] for name in predefined_names]
#             )
            
#             last_refresh_time = datetime.now()
#             api_logger.info("Precomputed embeddings for all issues")
#             return True
            
#         except Exception as e:
#             api_logger.error(f"Error loading issues: {str(e)}", exc_info=True)
#             return False

# @api_bp.before_app_request
# def initialize_issues():
#     """Load issues on first request and start auto-refresh thread"""
#     global predefined_issues, last_refresh_time
    
#     # Load issues if not already loaded
#     if not predefined_issues:
#         if load_issues_from_db():
#             api_logger.info("Initial issues loaded successfully")
#         else:
#             api_logger.error("Failed to load issues during initialization")
    
#     # Start auto-refresh thread only once
#     if not hasattr(initialize_issues, 'auto_refresh_started'):
#         refresh_thread = threading.Thread(
#             target=auto_refresh_issues, 
#             daemon=True,
#             name="AutoRefreshThread"
#         )
#         refresh_thread.start()
#         initialize_issues.auto_refresh_started = True
#         api_logger.info("Started automatic daily refresh thread")

# def auto_refresh_issues():
#     """Automatically refresh issues once per day"""
#     global last_refresh_time
#     while True:
#         try:
#             current_time = datetime.now()
            
#             # Check if it's time to refresh (once per day or never refreshed)
#             if (last_refresh_time is None or 
#                 current_time - last_refresh_time > timedelta(hours=refresh_interval_hours)):
                
#                 api_logger.info(f"Auto-refresh triggered at {current_time}")
#                 if load_issues_from_db():
#                     api_logger.info(f"Auto-refresh completed. Next refresh in {refresh_interval_hours} hours")
#                 else:
#                     api_logger.warning("Auto-refresh failed, will retry in 1 hour")
#                     time.sleep(3600)  # Wait 1 hour before retrying
#                     continue
            
#             # Sleep for 1 hour and check again
#             time.sleep(3600)
            
#         except Exception as e:
#             api_logger.error(f"Error in auto-refresh thread: {str(e)}", exc_info=True)
#             time.sleep(3600)  # Wait 1 hour before retrying

# def _save_mapping(user_input, issue_name, score, issue_id, ticket_type):
#     """Helper function to save mapping results to Excel"""
#     try:
#         new_entry = pd.DataFrame([{
#             'User_Issue': user_input,
#             'Mapped_Issue': issue_name,
#             'Score': score,
#             'Issue_ID': issue_id,
#             'Ticket_Type': ticket_type,
#             'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         }])
        
#         os.makedirs(os.path.dirname(config.SAVE_PATH), exist_ok=True)
        
#         if os.path.exists(config.SAVE_PATH):
#             existing = pd.read_excel(config.SAVE_PATH)
#             updated = pd.concat([existing, new_entry], ignore_index=True)
#         else:
#             updated = new_entry
            
#         updated.to_excel(config.SAVE_PATH, index=False)
#         api_logger.info(f"Saved mapping to Excel: '{user_input}' -> '{issue_name}' (score: {score:.2f})")
        
#     except Exception as e:
#         api_logger.error(f"Error saving to Excel: {str(e)}", exc_info=True)

# # @api_bp.route('/predict', methods=['POST'])
# # def predict():
# #     try:
# #         api_logger.info(f"predict endpoint called URL: {request.url}")
        
# #         if not request.is_json:
# #             api_logger.warning("Predict endpoint called without JSON data")
# #             return jsonify({'error': 'Request must be JSON'}), 400
        
# #         user_input = request.args.get('issue', '').strip()
# #         api_logger.info(f"Received prediction request: '{user_input}'")
        
# #         if not user_input:
# #             api_logger.warning("Empty issue received in prediction request")
# #             return jsonify({'error': 'Please enter an issue.'}), 400
        
# #         if not predefined_issues:
# #             api_logger.error("No predefined issues available for prediction")
# #             return jsonify({'error': 'No predefined issues available. Please check the database.'}), 500
        
# #         best_match_idx, best_score = similarity_service.find_best_match(
# #             user_input, predefined_issues, predefined_embeddings
# #         )
# #         best_match_issue = predefined_issues[best_match_idx]
        
# #         issue_id = best_match_issue[0]
# #         issue_name = best_match_issue[1]
# #         ticket_type = best_match_issue[2]
        
# #         api_logger.info(f"Best match found: '{issue_name}' with score {best_score:.2f}")
        
# #         if best_score >= config.SIMILARITY_THRESHOLD:
# #             # Save to Excel
# #             _save_mapping(user_input, issue_name, best_score, issue_id, ticket_type)
            
# #             response_data = {
# #                 'user_input': user_input,
# #                 'predicted_category': issue_name,
# #                 'similarity_score': round(best_score, 2),
# #                 'issue_id': issue_id,
# #                 'ticket_type': ticket_type
# #             }
            
# #             api_logger.info(f"Prediction successful: {response_data}")
# #             return jsonify(response_data)
# #         else:
# #             api_logger.warning(f"Low similarity score: {best_score:.2f} for input: '{user_input}'")
# #             return jsonify({
# #                 'error': 'Please enter a more valid issue or select from the dropdown.',
# #                 'score': round(best_score, 2)
# #             })
            
# #     except Exception as e:
# #         api_logger.error(f"Error in predict endpoint: {str(e)}", exc_info=True)
# #         return jsonify({'error': 'Internal server error'}), 500

# @api_bp.route("/all_issues", methods=['GET'])
# def all_issues():
#     try:
#         api_logger.info(f"All_issues endpoint called URL: {request.url}")
        
#         if not predefined_issues:
#             api_logger.warning("No predefined issues available")
#             return jsonify([])
        
#         result = []
#         for issue in predefined_issues:
#             result.append({
#                 "id": issue[0],        
#                 "name": issue[1],
#                 "ticketType": issue[2],
#             })
        
#         result.sort(key=lambda x: x['name'])
#         api_logger.info(f"Returning {len(result)} issues")
#         return jsonify(result)
        
#     except Exception as e:
#         api_logger.error(f"Error in all_issues endpoint: {str(e)}", exc_info=True)
#         return jsonify({'error': 'Internal server error'}), 500

# @api_bp.route("/search_issues", methods=['GET'])
# def search_issues():
#     try:
#         user_input = request.args.get('issue', '').strip()
#         api_logger.info(f"Search_issues endpoint called with URL: {request.url}, query: '{user_input}'")
#         if not predefined_issues:
#             api_logger.warning("No predefined issues available for search")
#             return jsonify([])
        
#         if not user_input:
#             api_logger.info("Empty search query, returning all issues")
#             result = []
#             for issue in predefined_issues:
#                 result.append({
#                     "id": issue[0],          
#                     "name": issue[1],        
#                     "type": issue[2], 
#                     "score": 1.0
#                 })
#             result.sort(key=lambda x: x['name'])
#             api_logger.info(f"Returning all {len(result)} issues for empty search")
#             return jsonify(result)
        
#         user_embedding = similarity_service.encode_text(user_input)
#         cos_scores = similarity_service.calculate_similarity(user_embedding, predefined_embeddings)
        
#         result = []
#         for idx, score in enumerate(cos_scores):
#             score_value = score.item()
#             if score_value > config.MIN_SEARCH_SCORE:
#                 issue_id = predefined_issues[idx][0]  
#                 issue_name = predefined_issues[idx][1] 
#                 ticket_type = predefined_issues[idx][2]  
                
#                 result.append({
#                     "id": issue_id,          
#                     "name": issue_name,        
#                     "type": ticket_type, 
#                     "score": round(score_value, 4)  
#                 })
        
#         result.sort(key=lambda x: x['score'], reverse=True)
#         api_logger.info(f"Search found {len(result)} matches for query: '{user_input}'")
#         return jsonify(result)
        
#     except Exception as e:
#         api_logger.error(f"Error in search_issues endpoint: {str(e)}", exc_info=True)
#         return jsonify({'error': 'Internal server error'}), 500

# @api_bp.route("/refresh_issues", methods=['GET'])
# def refresh_issues():
#     """Manual endpoint to refresh issues from database"""
#     try:
#         api_logger.info("Manual refresh requested")
#         success = load_issues_from_db()
        
#         if success:
#             return jsonify({
#                 'status': 'success',
#                 'message': f'Refreshed {len(predefined_issues)} issues',
#                 'issues_count': len(predefined_issues),
#                 'last_refresh': last_refresh_time.isoformat() if last_refresh_time else None
#             }), 200
#         else:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Failed to refresh issues from database'
#             }), 500
        
#     except Exception as e:
#         api_logger.error(f"Error in manual refresh: {str(e)}", exc_info=True)
#         return jsonify({'error': 'Refresh failed'}), 500

# # Add error handler for the blueprint
# @api_bp.errorhandler(404)
# def not_found(error):
#     api_logger.warning(f"404 error: {request.url}")
#     return jsonify({'error': 'Endpoint not found'}), 404

# @api_bp.errorhandler(500)
# def internal_error(error):
#     api_logger.error(f"500 error: {str(error)}")
#     return jsonify({'error': 'Internal server error'}), 500


# @api_bp.route('/predict', methods=['POST'])
# def predict():
#     try:
#         api_logger.info(f"predict endpoint called URL: {request.url}")

#         if not request.is_json:
#             api_logger.warning("Predict endpoint called without JSON data")
#             return jsonify({'error': 'Request must be JSON'}), 400

#         # Get user inputs
#         user_input = request.args.get('issue', '').strip()
#         ticket_type_arg = request.args.get('ticketType', '').strip()

#         # Convert ticketType to int if possible
#         selected_ticket_type = int(ticket_type_arg) if ticket_type_arg.isdigit() else None

#         api_logger.info(
#             f"Received prediction request: issue='{user_input}', ticketType={selected_ticket_type}"
#         )

#         if not user_input:
#             api_logger.warning("Empty issue received in prediction request")
#             return jsonify({'error': 'Please enter an issue.'}), 400

#         if not predefined_issues:
#             api_logger.error("No predefined issues available for prediction")
#             return jsonify({'error': 'No predefined issues available. Please check the database.'}), 500

#         # Filter by ticketType if provided
#         if selected_ticket_type is not None:
#             filtered_issues = []
#             filtered_embeddings = []

#             for i, issue in enumerate(predefined_issues):
#                 if issue[2] == selected_ticket_type:  # assuming issue[2] is ticketType
#                     filtered_issues.append(issue)
#                     filtered_embeddings.append(predefined_embeddings[i])

#             if not filtered_issues:
#                 api_logger.warning(f"No issues found for ticketType={selected_ticket_type}")
#                 return jsonify({
#                     'error': f'No predefined issues available for ticket type {selected_ticket_type}'
#                 }), 404

#             search_issues = filtered_issues
#             search_embeddings = filtered_embeddings
#         else:
#             search_issues = predefined_issues
#             search_embeddings = predefined_embeddings

#         # Find best match
#         best_match_idx, best_score = similarity_service.find_best_match(
#             user_input, search_issues, search_embeddings
#         )
#         best_match_issue = search_issues[best_match_idx]

#         issue_id = best_match_issue[0]
#         issue_name = best_match_issue[1]
#         ticket_type = best_match_issue[2]

#         api_logger.info(f"Best match found: '{issue_name}' with score {best_score:.2f}")

#         if best_score >= config.SIMILARITY_THRESHOLD:
#             _save_mapping(user_input, issue_name, best_score, issue_id, ticket_type)

#             response_data = {
#                 'user_input': user_input,
#                 'predicted_category': issue_name,
#                 'similarity_score': round(best_score, 2),
#                 'issue_id': issue_id,
#                 'ticket_type': ticket_type
#             }
#             api_logger.info(f"Prediction successful: {response_data}")
#             return jsonify(response_data)

#         else:
#             api_logger.warning(
#                 f"Low similarity score: {best_score:.2f} for input: '{user_input}'"
#             )
#             return jsonify({
#                 'error': 'Please enter a more valid issue or select from the dropdown.',
#                 'score': round(best_score, 2)
#             })

#     except Exception as e:
#         api_logger.error(f"Error in predict endpoint: {str(e)}", exc_info=True)
#         return jsonify({'error': 'Internal server error'}), 500

from flask import Blueprint, jsonify, request
import pandas as pd
import os
import torch
import threading
import time
import logging
from datetime import datetime, timedelta
from app.services.database import db_service
from app.services.similarity_service import similarity_service
from app.utils.config import config
from app.utils.loggin_config import get_logger   # ✅ import centralized logging

logger = get_logger("api")

api_bp = Blueprint("api", __name__)

# Global caching variables
predefined_issues = []
predefined_embeddings = None
last_refresh_time = None
refresh_interval_hours = 24
refresh_lock = threading.Lock()


def load_issues_from_db():
    """Load issues from DB and update embeddings (thread-safe)."""
    global predefined_issues, predefined_embeddings, last_refresh_time
    with refresh_lock:
        try:
            logger.info("Loading predefined issues from database")
            issues = db_service.get_known_issues()
            if not issues:
                logger.warning("No predefined issues found")
                return False

            predefined_issues[:] = issues
            names = [issue[1] for issue in predefined_issues]
            similarity_service.update_embeddings(names)
            predefined_embeddings = torch.stack(
                [similarity_service.issue_embeddings_cache[name] for name in names]
            )

            last_refresh_time = datetime.now()
            logger.info(f"Loaded {len(predefined_issues)} issues and updated embeddings")
            return True
        except Exception as e:
            logger.error(f"Failed to load issues: {e}", exc_info=True)
            return False


@api_bp.before_app_request
def initialize_issues():
    """Load issues at first request and start auto-refresh thread."""
    global predefined_issues
    if not predefined_issues:
        if load_issues_from_db():
            logger.info("Initial issues loaded successfully")
        else:
            logger.error("Failed to load issues during initialization")

    if not hasattr(initialize_issues, "auto_refresh_started"):
        thread = threading.Thread(target=auto_refresh_issues, daemon=True, name="AutoRefreshThread")
        thread.start()
        initialize_issues.auto_refresh_started = True
        logger.info("Started auto-refresh thread")


def auto_refresh_issues():
    """Automatically refresh issues once per day."""
    global last_refresh_time
    while True:
        try:
            now = datetime.now()
            if last_refresh_time is None or (now - last_refresh_time) > timedelta(hours=refresh_interval_hours):
                logger.info("Auto-refresh triggered")
                if load_issues_from_db():
                    logger.info("Auto-refresh completed successfully")
                else:
                    logger.warning("Auto-refresh failed; will retry in 1 hour")
                    time.sleep(3600)
                    continue
            time.sleep(3600)
        except Exception as e:
            logger.error(f"Error in auto-refresh thread: {e}", exc_info=True)
            time.sleep(3600)


def _save_mapping(user_input, issue_name, score, issue_id, ticket_type):
    """Save mapping to Excel."""
    try:
        entry = pd.DataFrame([{
            "User_Issue": user_input,
            "Mapped_Issue": issue_name,
            "Score": score,
            "Issue_ID": issue_id,
            "Ticket_Type": ticket_type,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        os.makedirs(os.path.dirname(config.SAVE_PATH), exist_ok=True)
        if os.path.exists(config.SAVE_PATH):
            df = pd.read_excel(config.SAVE_PATH)
            df = pd.concat([df, entry], ignore_index=True)
        else:
            df = entry
        df.to_excel(config.SAVE_PATH, index=False)
        logger.info(f"Saved mapping: '{user_input}' -> '{issue_name}' (score: {score:.2f})")
    except Exception as e:
        logger.error(f"Failed to save mapping to Excel: {e}", exc_info=True)


# ----------- API Routes -----------

@api_bp.route("/all_issues", methods=["GET"])
def all_issues():
    try:
        logger.info(f"/all_issues called: {request.url}")
        if not predefined_issues:
            logger.warning("No issues available")
            return jsonify([])

        result = [{"id": i[0], "name": i[1], "ticketType": i[2]} for i in predefined_issues]
        result.sort(key=lambda x: x["name"])
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /all_issues: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/search_issues", methods=["GET"])
def search_issues():
    try:
        query = request.args.get("issue", "").strip()
        logger.info(f"/search_issues called with query: '{query}'")
        if not predefined_issues:
            return jsonify([])

        if not query:
            return jsonify([{"id": i[0], "name": i[1], "type": i[2], "score": 1.0} for i in predefined_issues])

        user_emb = similarity_service.encode_text(query)
        scores = similarity_service.calculate_similarity(user_emb, predefined_embeddings)

        result = []
        for idx, score in enumerate(scores):
            score_val = score.item()
            if score_val >= config.MIN_SEARCH_SCORE:
                issue = predefined_issues[idx]
                result.append({"id": issue[0], "name": issue[1], "type": issue[2], "score": round(score_val, 4)})

        result.sort(key=lambda x: x["score"], reverse=True)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /search_issues: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/refresh_issues", methods=["GET"])
def refresh_issues():
    try:
        logger.info("Manual refresh requested")
        success = load_issues_from_db()
        if success:
            return jsonify({
                "status": "success",
                "issues_count": len(predefined_issues),
                "last_refresh": last_refresh_time.isoformat() if last_refresh_time else None
            })
        return jsonify({"status": "error", "message": "Failed to refresh issues"}), 500
    except Exception as e:
        logger.error(f"Error in /refresh_issues: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/predict", methods=["POST"])
def predict():
    try:
        logger.info(f"/predict called: {request.url}")
        # if not request.is_json:
        #     logger.warning("Predict called without JSON")
        #     return jsonify({"error": "Request must be JSON"}), 400

        user_input = request.args.get("issue", "").strip()
        ticket_type_arg = request.args.get("ticketType", "").strip()
        ticket_type = int(ticket_type_arg) if ticket_type_arg.isdigit() else None
        logger.info(f"Received prediction: issue='{user_input}', ticketType={ticket_type}")

        if not user_input:
            return jsonify({"error": "Please enter an issue."}), 400
        if not predefined_issues:
            return jsonify({"error": "No predefined issues available."}), 500

        # Filter issues by ticketType if provided
        if ticket_type is not None:
            filtered_issues = [i for idx, i in enumerate(predefined_issues) if i[2] == ticket_type]
            filtered_embeddings = [predefined_embeddings[idx] for idx, i in enumerate(predefined_issues) if i[2] == ticket_type]
            if not filtered_issues:
                return jsonify({"error": f"No issues available for ticket type {ticket_type}"})
        else:
            filtered_issues = predefined_issues
            filtered_embeddings = predefined_embeddings

        best_idx, best_score = similarity_service.find_best_match(user_input, filtered_issues, filtered_embeddings)
        best_issue = filtered_issues[best_idx]
        issue_id, issue_name, ticket_type = best_issue[0], best_issue[1], best_issue[2]

        logger.info(f"Best match: '{issue_name}' score={best_score:.2f}")

        if best_score >= config.SIMILARITY_THRESHOLD:
            _save_mapping(user_input, issue_name, best_score, issue_id, ticket_type)
            return jsonify({
                "user_input": user_input,
                "predicted_category": issue_name,
                "similarity_score": round(best_score, 2),
                "issue_id": issue_id,
                "ticket_type": ticket_type
            })

        return jsonify({
            "error": "Please enter a more valid issue or select from the dropdown.",
            "score": round(best_score, 2)
        })
    except Exception as e:
        logger.error(f"Error in /predict: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    
@api_bp.route("healthz/", methods=["GET"])
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