# import torch
# from sentence_transformers import SentenceTransformer, util
# from ..utils.config import config
# import logging
# logger = logging.getLogger(__name__)

# class SimilarityService:
#     def __init__(self):
#         self.model = SentenceTransformer(config.MODEL_NAME)
#         self.issue_embeddings_cache = {}
    
#     def encode_text(self, text):
#         return self.model.encode(text, convert_to_tensor=True)
    
#     def update_embeddings(self, issues):
#         for issue in issues:
#             if issue not in self.issue_embeddings_cache:
#                 self.issue_embeddings_cache[issue] = self.encode_text(issue)
    
#     # def calculate_similarity(self, user_embedding, predefined_embeddings):
#     #     return util.pytorch_cos_sim(user_embedding, predefined_embeddings)[0]
    
#     def calculate_similarity(self, user_embedding, predefined_embeddings):
#     # Ensure tensors
#         if isinstance(predefined_embeddings, list):
#             predefined_embeddings = torch.stack(predefined_embeddings)

#         # Ensure shape (1, d) for user_embedding
#         if len(user_embedding.shape) == 1:
#             user_embedding = user_embedding.unsqueeze(0)

#         cos_scores = util.pytorch_cos_sim(user_embedding, predefined_embeddings)
#         cos_scores = cos_scores.view(-1)  # flatten to 1D
#         return cos_scores


#     def find_best_match(self, user_input, predefined_issues, predefined_embeddings):
#         user_embedding = self.encode_text(user_input)
#         cos_scores = self.calculate_similarity(user_embedding, predefined_embeddings)

#         # convert to numpy scalars
#         if hasattr(cos_scores, "detach"):
#             cos_scores = cos_scores.detach().cpu().numpy()

#         best_match_idx = int(cos_scores.argmax())
#         best_score = float(cos_scores[best_match_idx])
#         return best_match_idx, best_score


    
#     # def find_best_match(self, user_input, predefined_issues, predefined_embeddings):
#     #     user_embedding = self.encode_text(user_input)
#     #     cos_scores = self.calculate_similarity(user_embedding, predefined_embeddings)
#     #     best_match_idx = cos_scores.argmax().item()
#     #     best_score = cos_scores[best_match_idx].item()
#     #     return best_match_idx, best_score

# similarity_service = SimilarityService()
import torch
import logging
from sentence_transformers import SentenceTransformer, util
from ..utils.config import config
logger = logging.getLogger(__name__)

# Alias for Exception
Error = Exception


class SimilarityService:
    """
    A service for encoding text into embeddings and computing similarity
    between user input and predefined issues.
    """

    def __init__(self):
        try:
            self.model = SentenceTransformer(config.MODEL_NAME)
            logger.info(f"Loaded SentenceTransformer model: {config.MODEL_NAME}")
        except Error as e:
            logger.error(f"Failed to load model {config.MODEL_NAME}: {e}")
            raise

        self.issue_embeddings_cache = {}

    def encode_text(self, text: str):
        """
        Encode text into an embedding tensor.
        """
        try:
            return self.model.encode(text, convert_to_tensor=True)
        except Error as e:
            logger.error(f"Encoding failed for text='{text}': {e}")
            raise

    def update_embeddings(self, issues):
        """
        Update cache with embeddings for new issues.
        """
        for issue in issues:
            if issue not in self.issue_embeddings_cache:
                self.issue_embeddings_cache[issue] = self.encode_text(issue)
                logger.debug(f"Cached embedding for issue: {issue}")

    def calculate_similarity(self, user_embedding, predefined_embeddings):
        """
        Calculate cosine similarity between a user embedding and predefined embeddings.
        """
        try:
            # Ensure tensors
            if isinstance(predefined_embeddings, list):
                predefined_embeddings = torch.stack(predefined_embeddings)

            # Ensure shape (1, d) for user_embedding
            if len(user_embedding.shape) == 1:
                user_embedding = user_embedding.unsqueeze(0)

            cos_scores = util.pytorch_cos_sim(user_embedding, predefined_embeddings)
            cos_scores = cos_scores.view(-1)  # flatten to 1D
            return cos_scores
        except Error as e:
            logger.error(f"Error calculating similarity: {e}")
            raise

    def find_best_match(self, user_input, predefined_issues, predefined_embeddings):
        """
        Find the best match for a user input from predefined issues.
        Returns: (best_match_idx, best_score)
        """
        try:
            user_embedding = self.encode_text(user_input)
            cos_scores = self.calculate_similarity(user_embedding, predefined_embeddings)

            # Convert to numpy scalars
            if hasattr(cos_scores, "detach"):
                cos_scores = cos_scores.detach().cpu().numpy()

            best_match_idx = int(cos_scores.argmax())
            best_score = float(cos_scores[best_match_idx])

            logger.info(
                f"Best match for '{user_input}' -> '{predefined_issues[best_match_idx]}' "
                f"(score={best_score:.4f})"
            )

            return best_match_idx, best_score
        except Error as e:
            logger.error(f"Failed to find best match for input='{user_input}': {e}")
            raise


# Global service instance
similarity_service = SimilarityService()
