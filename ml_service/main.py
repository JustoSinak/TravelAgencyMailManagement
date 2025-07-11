import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
from recommendation_engine import recommendation_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("Could not download NLTK data")

app = FastAPI(
    title="Email Classification ML Service",
    description="Machine Learning service for email classification and recommendations",
    version="1.0.0"
)

# Global variables for model and vectorizer
model_pipeline = None
category_names = {
    0: "General",
    1: "Booking",
    2: "Customer Service", 
    3: "Marketing",
    4: "Technical Support",
    5: "Billing",
    6: "Complaint",
    7: "Inquiry"
}

class EmailData(BaseModel):
    subject: str
    body: str
    sender: str

class ClassificationResponse(BaseModel):
    category_id: int
    category_name: str
    confidence: float
    probabilities: Dict[str, float]

class UserActionData(BaseModel):
    user_id: int
    email_id: int
    action_type: str
    metadata: Dict[str, Any] = {}

class EmailFeatureData(BaseModel):
    email_id: int
    subject: str
    body: str
    sender: str
    categories: List[str] = []

class RecommendationRequest(BaseModel):
    user_id: int
    num_recommendations: int = 5

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    user_id: int
    total_recommendations: int

def preprocess_text(text: str) -> str:
    """Preprocess text for ML model"""
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Stem words
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        
        return ' '.join(tokens)
    except Exception as e:
        logger.warning(f"Error in text preprocessing: {e}")
        return text.lower()

def create_sample_training_data():
    """Create sample training data for the model"""
    training_data = [
        ("Book flight to Paris", "I would like to book a flight to Paris for next week", "Booking"),
        ("Hotel reservation", "Please help me reserve a hotel room", "Booking"),
        ("Cancel my booking", "I need to cancel my reservation", "Customer Service"),
        ("Special offer", "Check out our amazing deals", "Marketing"),
        ("Website not working", "I can't access my account", "Technical Support"),
        ("Payment issue", "My credit card was charged twice", "Billing"),
        ("Terrible service", "I'm very disappointed with the service", "Complaint"),
        ("Travel information", "What documents do I need for travel?", "Inquiry"),
        ("Flight confirmation", "Please confirm my flight booking", "Booking"),
        ("Refund request", "I want a refund for my cancelled trip", "Billing"),
        ("Lost luggage", "My luggage is missing", "Customer Service"),
        ("Newsletter", "Subscribe to our travel newsletter", "Marketing"),
        ("App crashes", "The mobile app keeps crashing", "Technical Support"),
        ("Poor hotel quality", "The hotel room was dirty", "Complaint"),
        ("Visa requirements", "What visa do I need for this country?", "Inquiry"),
        ("Thank you", "Thanks for the excellent service", "General"),
    ]
    
    texts = []
    labels = []
    
    for subject, body, category in training_data:
        combined_text = f"{subject} {body}"
        texts.append(combined_text)
        labels.append(category)
    
    return texts, labels

def train_model():
    """Train the classification model"""
    try:
        logger.info("Training classification model...")
        
        # Get training data
        texts, labels = create_sample_training_data()
        
        # Create label mapping
        unique_labels = list(set(labels))
        label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
        id_to_label = {idx: label for label, idx in label_to_id.items()}
        
        # Convert labels to numeric
        numeric_labels = [label_to_id[label] for label in labels]
        
        # Preprocess texts
        processed_texts = [preprocess_text(text) for text in texts]
        
        # Create pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB(alpha=1.0))
        ])
        
        # Train model
        pipeline.fit(processed_texts, numeric_labels)
        
        # Save model and mappings
        joblib.dump(pipeline, 'email_classifier.pkl')
        joblib.dump(id_to_label, 'label_mapping.pkl')
        
        logger.info("Model training completed successfully")
        return pipeline, id_to_label
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise

def load_model():
    """Load the trained model"""
    global model_pipeline, category_names
    
    try:
        if os.path.exists('email_classifier.pkl') and os.path.exists('label_mapping.pkl'):
            model_pipeline = joblib.load('email_classifier.pkl')
            category_names = joblib.load('label_mapping.pkl')
            logger.info("Model loaded successfully")
        else:
            logger.info("No existing model found, training new model...")
            model_pipeline, category_names = train_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # Train a new model if loading fails
        model_pipeline, category_names = train_model()

# Load model on startup
load_model()

@app.on_event("startup")
async def startup_event():
    """Initialize the ML service"""
    logger.info("ML Service starting up...")
    if model_pipeline is None:
        load_model()

    # Load recommendation model
    recommendation_engine.load_model("recommendation_model.pkl")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Email Classification ML Service", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model_pipeline is not None,
        "categories": list(category_names.values()) if category_names else []
    }

@app.post("/classify/", response_model=ClassificationResponse)
async def classify_email(email_data: EmailData):
    """Classify an email into categories"""
    try:
        if model_pipeline is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Combine email features
        combined_text = f"{email_data.subject} {email_data.body}"
        
        # Preprocess text
        processed_text = preprocess_text(combined_text)
        
        # Make prediction
        prediction = model_pipeline.predict([processed_text])[0]
        probabilities = model_pipeline.predict_proba([processed_text])[0]
        
        # Get category name
        category_name = category_names.get(prediction, "Unknown")
        confidence = float(probabilities.max())
        
        # Create probability dictionary
        prob_dict = {
            category_names.get(i, f"Category_{i}"): float(prob) 
            for i, prob in enumerate(probabilities)
        }
        
        logger.info(f"Classified email: {category_name} (confidence: {confidence:.3f})")
        
        return ClassificationResponse(
            category_id=int(prediction),
            category_name=category_name,
            confidence=confidence,
            probabilities=prob_dict
        )
        
    except Exception as e:
        logger.error(f"Error classifying email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrain/")
async def retrain_model():
    """Retrain the model with new data"""
    try:
        global model_pipeline, category_names
        model_pipeline, category_names = train_model()
        return {"message": "Model retrained successfully"}
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/")
async def get_categories():
    """Get available categories"""
    return {"categories": category_names}

@app.post("/record-action/")
async def record_user_action(action_data: UserActionData):
    """Record a user action for recommendation learning"""
    try:
        recommendation_engine.record_action(
            user_id=action_data.user_id,
            email_id=action_data.email_id,
            action_type=action_data.action_type,
            metadata=action_data.metadata
        )
        return {"message": "Action recorded successfully"}
    except Exception as e:
        logger.error(f"Error recording action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-email-features/")
async def add_email_features(email_data: EmailFeatureData):
    """Add email features for content-based recommendations"""
    try:
        recommendation_engine.add_email_features(
            email_id=email_data.email_id,
            subject=email_data.subject,
            body=email_data.body,
            sender=email_data.sender,
            categories=email_data.categories
        )
        return {"message": "Email features added successfully"}
    except Exception as e:
        logger.error(f"Error adding email features: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get email recommendations for a user"""
    try:
        recommendations = recommendation_engine.get_recommendations(
            user_id=request.user_id,
            num_recommendations=request.num_recommendations
        )

        return RecommendationResponse(
            recommendations=recommendations,
            user_id=request.user_id,
            total_recommendations=len(recommendations)
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-recommendation-model/")
async def save_recommendation_model():
    """Save the current recommendation model"""
    try:
        recommendation_engine.save_model("recommendation_model.pkl")
        return {"message": "Recommendation model saved successfully"}
    except Exception as e:
        logger.error(f"Error saving recommendation model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load-recommendation-model/")
async def load_recommendation_model():
    """Load the recommendation model"""
    try:
        recommendation_engine.load_model("recommendation_model.pkl")
        return {"message": "Recommendation model loaded successfully"}
    except Exception as e:
        logger.error(f"Error loading recommendation model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
