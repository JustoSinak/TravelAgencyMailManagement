import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import logging
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

logger = logging.getLogger(__name__)

class EmailRecommendationEngine:
    """
    Collaborative filtering recommendation engine for emails
    """
    
    def __init__(self):
        self.user_actions = defaultdict(list)
        self.email_features = {}
        self.user_similarity_matrix = {}
        self.item_similarity_matrix = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500)
        self.email_vectors = {}
        
    def record_action(self, user_id: int, email_id: int, action_type: str, metadata: Dict = None):
        """Record a user action for recommendation learning"""
        action_score = self._get_action_score(action_type)
        
        action_data = {
            'email_id': email_id,
            'action_type': action_type,
            'score': action_score,
            'metadata': metadata or {}
        }
        
        self.user_actions[user_id].append(action_data)
        
        # Update similarity matrices periodically
        if len(self.user_actions[user_id]) % 10 == 0:
            self._update_similarity_matrices()
    
    def _get_action_score(self, action_type: str) -> float:
        """Convert action type to numerical score"""
        action_scores = {
            'OPEN': 1.0,
            'REPLY': 3.0,
            'FORWARD': 2.0,
            'DELETE': -1.0,
            'MARK_IMPORTANT': 2.5,
            'CATEGORY_CHANGE': 1.5,
            'ARCHIVE': 0.5
        }
        return action_scores.get(action_type, 1.0)
    
    def add_email_features(self, email_id: int, subject: str, body: str, sender: str, categories: List[str]):
        """Add email features for content-based filtering"""
        combined_text = f"{subject} {body} {sender} {' '.join(categories)}"
        
        self.email_features[email_id] = {
            'text': combined_text,
            'subject': subject,
            'body': body,
            'sender': sender,
            'categories': categories
        }
    
    def _update_similarity_matrices(self):
        """Update user and item similarity matrices"""
        try:
            self._update_user_similarity()
            self._update_item_similarity()
            logger.info("Similarity matrices updated")
        except Exception as e:
            logger.error(f"Error updating similarity matrices: {e}")
    
    def _update_user_similarity(self):
        """Update user-user similarity matrix using collaborative filtering"""
        users = list(self.user_actions.keys())
        if len(users) < 2:
            return
        
        # Create user-item matrix
        all_emails = set()
        for actions in self.user_actions.values():
            for action in actions:
                all_emails.add(action['email_id'])
        
        all_emails = list(all_emails)
        user_item_matrix = np.zeros((len(users), len(all_emails)))
        
        for i, user_id in enumerate(users):
            for action in self.user_actions[user_id]:
                if action['email_id'] in all_emails:
                    j = all_emails.index(action['email_id'])
                    user_item_matrix[i, j] += action['score']
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(user_item_matrix)
        
        # Store similarity scores
        for i, user1 in enumerate(users):
            self.user_similarity_matrix[user1] = {}
            for j, user2 in enumerate(users):
                if i != j:
                    self.user_similarity_matrix[user1][user2] = similarity_matrix[i, j]
    
    def _update_item_similarity(self):
        """Update item-item similarity matrix using content-based filtering"""
        if not self.email_features:
            return
        
        email_ids = list(self.email_features.keys())
        texts = [self.email_features[email_id]['text'] for email_id in email_ids]
        
        try:
            # Fit TF-IDF vectorizer and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Store email vectors
            for i, email_id in enumerate(email_ids):
                self.email_vectors[email_id] = tfidf_matrix[i]
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Store similarity scores
            for i, email1 in enumerate(email_ids):
                if email1 not in self.item_similarity_matrix:
                    self.item_similarity_matrix[email1] = {}
                for j, email2 in enumerate(email_ids):
                    if i != j:
                        self.item_similarity_matrix[email1][email2] = similarity_matrix[i, j]
        
        except Exception as e:
            logger.error(f"Error updating item similarity: {e}")
    
    def get_recommendations(self, user_id: int, num_recommendations: int = 5) -> List[Dict]:
        """Get email recommendations for a user"""
        try:
            # Combine collaborative and content-based recommendations
            collaborative_recs = self._get_collaborative_recommendations(user_id, num_recommendations)
            content_recs = self._get_content_based_recommendations(user_id, num_recommendations)
            
            # Merge and rank recommendations
            all_recs = {}
            
            # Add collaborative filtering scores
            for email_id, score in collaborative_recs:
                all_recs[email_id] = all_recs.get(email_id, 0) + score * 0.6
            
            # Add content-based scores
            for email_id, score in content_recs:
                all_recs[email_id] = all_recs.get(email_id, 0) + score * 0.4
            
            # Sort by combined score
            sorted_recs = sorted(all_recs.items(), key=lambda x: x[1], reverse=True)
            
            # Format recommendations
            recommendations = []
            for email_id, score in sorted_recs[:num_recommendations]:
                recommendations.append({
                    'email_id': email_id,
                    'score': float(score),
                    'reason': self._get_recommendation_reason(user_id, email_id)
                })
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def _get_collaborative_recommendations(self, user_id: int, num_recs: int) -> List[Tuple[int, float]]:
        """Get recommendations using collaborative filtering"""
        if user_id not in self.user_similarity_matrix:
            return []
        
        recommendations = defaultdict(float)
        user_actions_set = {action['email_id'] for action in self.user_actions[user_id]}
        
        # Find similar users
        similar_users = self.user_similarity_matrix[user_id]
        
        for similar_user_id, similarity_score in similar_users.items():
            if similarity_score > 0.1:  # Threshold for similarity
                for action in self.user_actions[similar_user_id]:
                    email_id = action['email_id']
                    if email_id not in user_actions_set:  # Don't recommend already seen emails
                        recommendations[email_id] += similarity_score * action['score']
        
        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:num_recs]
    
    def _get_content_based_recommendations(self, user_id: int, num_recs: int) -> List[Tuple[int, float]]:
        """Get recommendations using content-based filtering"""
        if user_id not in self.user_actions:
            return []
        
        # Get user's preferred email types based on actions
        user_preferences = defaultdict(float)
        user_actions_set = {action['email_id'] for action in self.user_actions[user_id]}
        
        for action in self.user_actions[user_id]:
            email_id = action['email_id']
            if email_id in self.email_features:
                categories = self.email_features[email_id]['categories']
                for category in categories:
                    user_preferences[category] += action['score']
        
        # Find emails similar to user preferences
        recommendations = defaultdict(float)
        
        for email_id, features in self.email_features.items():
            if email_id not in user_actions_set:
                score = 0
                for category in features['categories']:
                    score += user_preferences.get(category, 0)
                
                if score > 0:
                    recommendations[email_id] = score
        
        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:num_recs]
    
    def _get_recommendation_reason(self, user_id: int, email_id: int) -> str:
        """Get explanation for why this email was recommended"""
        reasons = []
        
        # Check collaborative filtering reason
        if user_id in self.user_similarity_matrix:
            similar_users = [uid for uid, score in self.user_similarity_matrix[user_id].items() if score > 0.1]
            if similar_users:
                reasons.append("Users with similar preferences liked this")
        
        # Check content-based reason
        if email_id in self.email_features:
            categories = self.email_features[email_id]['categories']
            if categories:
                reasons.append(f"Related to your interests in {', '.join(categories[:2])}")
        
        return "; ".join(reasons) if reasons else "Recommended for you"
    
    def save_model(self, filepath: str):
        """Save the recommendation model"""
        try:
            model_data = {
                'user_actions': dict(self.user_actions),
                'email_features': self.email_features,
                'user_similarity_matrix': self.user_similarity_matrix,
                'item_similarity_matrix': self.item_similarity_matrix
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Recommendation model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """Load the recommendation model"""
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.user_actions = defaultdict(list, model_data.get('user_actions', {}))
                self.email_features = model_data.get('email_features', {})
                self.user_similarity_matrix = model_data.get('user_similarity_matrix', {})
                self.item_similarity_matrix = model_data.get('item_similarity_matrix', {})
                logger.info(f"Recommendation model loaded from {filepath}")
            else:
                logger.info("No existing recommendation model found")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

# Global recommendation engine instance
recommendation_engine = EmailRecommendationEngine()
