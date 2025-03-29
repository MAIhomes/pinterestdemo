import os
import pandas as pd
import json
import sqlite3
import random
import requests
from urllib.parse import urlparse
from datetime import datetime
import re

from recommendation_system import RecommendationSystem

class UserPreferenceTracker:
    def __init__(self, db_path='data/bathroom_images.db'):
        """Initialize the user preference tracker with database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.recommender = RecommendationSystem(db_path)
    
    def get_user_preferences(self, user_id):
        """Get all preferences for a specific user."""
        self.cursor.execute('''
        SELECT p.*, i.category, i.description 
        FROM user_preferences p
        JOIN images i ON p.image_id = i.id
        WHERE p.user_id = ?
        ORDER BY p.timestamp DESC
        ''', (user_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_category_preferences(self, user_id):
        """Get category preferences for a specific user."""
        self.cursor.execute('''
        SELECT category, preference_score 
        FROM category_preferences
        WHERE user_id = ?
        ORDER BY preference_score DESC
        ''', (user_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_view_history(self, user_id, limit=50):
        """Get view history for a specific user."""
        self.cursor.execute('''
        SELECT s.*, i.category, i.description 
        FROM user_sessions s
        JOIN images i ON s.image_id = i.id
        WHERE s.user_id = ?
        ORDER BY s.timestamp DESC
        LIMIT ?
        ''', (user_id, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_preference_insights(self, user_id):
        """Get insights about user preferences."""
        # Get total interactions
        self.cursor.execute('''
        SELECT COUNT(*) as total FROM user_preferences
        WHERE user_id = ?
        ''', (user_id,))
        total_interactions = self.cursor.fetchone()['total']
        
        # Get likes count
        self.cursor.execute('''
        SELECT COUNT(*) as likes FROM user_preferences
        WHERE user_id = ? AND rating > 0
        ''', (user_id,))
        likes = self.cursor.fetchone()['likes']
        
        # Get dislikes count
        self.cursor.execute('''
        SELECT COUNT(*) as dislikes FROM user_preferences
        WHERE user_id = ? AND rating < 0
        ''', (user_id,))
        dislikes = self.cursor.fetchone()['dislikes']
        
        # Get favorite category
        self.cursor.execute('''
        SELECT category FROM category_preferences
        WHERE user_id = ?
        ORDER BY preference_score DESC
        LIMIT 1
        ''', (user_id,))
        result = self.cursor.fetchone()
        favorite_category = result['category'] if result else None
        
        # Get least favorite category
        self.cursor.execute('''
        SELECT category FROM category_preferences
        WHERE user_id = ?
        ORDER BY preference_score ASC
        LIMIT 1
        ''', (user_id,))
        result = self.cursor.fetchone()
        least_favorite_category = result['category'] if result else None
        
        # Get most viewed category
        self.cursor.execute('''
        SELECT i.category, COUNT(*) as view_count
        FROM user_sessions s
        JOIN images i ON s.image_id = i.id
        WHERE s.user_id = ?
        GROUP BY i.category
        ORDER BY view_count DESC
        LIMIT 1
        ''', (user_id,))
        result = self.cursor.fetchone()
        most_viewed_category = result['category'] if result else None
        
        return {
            'total_interactions': total_interactions,
            'likes': likes,
            'dislikes': dislikes,
            'favorite_category': favorite_category,
            'least_favorite_category': least_favorite_category,
            'most_viewed_category': most_viewed_category
        }
    
    def generate_personalized_recommendations(self, user_id, limit=5):
        """Generate personalized recommendations based on user preferences."""
        return self.recommender.get_personalized_recommendations(user_id, limit)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
        if self.recommender:
            self.recommender.close()

# Test function to demonstrate user preference tracking
def test_user_preference_tracking():
    """Test the user preference tracking functionality."""
    # Create a test user
    user_id = f"test_user_{random.randint(1000, 9999)}"
    session_id = f"test_session_{random.randint(1000, 9999)}"
    
    # Initialize the recommendation system and user preference tracker
    recommender = RecommendationSystem()
    tracker = UserPreferenceTracker()
    
    # Get some initial recommendations
    images = recommender.get_initial_recommendations(10)
    
    # Simulate user interactions
    for i, image in enumerate(images):
        # Like some images, dislike others
        rating = 1 if i % 3 != 0 else -1
        recommender.record_user_preference(user_id, image['id'], rating)
        
        # Record view time
        view_time = random.randint(2, 15)
        recommender.record_view_time(session_id, user_id, image['id'], view_time)
    
    # Update similarity scores
    recommender.update_similarity_scores(user_id)
    
    # Get user preferences
    preferences = tracker.get_user_preferences(user_id)
    print(f"User preferences: {len(preferences)} records")
    
    # Get category preferences
    category_prefs = tracker.get_category_preferences(user_id)
    print(f"Category preferences: {len(category_prefs)} categories")
    for pref in category_prefs:
        print(f"  {pref['category']}: {pref['preference_score']}")
    
    # Get view history
    view_history = tracker.get_view_history(user_id)
    print(f"View history: {len(view_history)} records")
    
    # Get preference insights
    insights = tracker.get_preference_insights(user_id)
    print("User preference insights:")
    print(f"  Total interactions: {insights['total_interactions']}")
    print(f"  Likes: {insights['likes']}")
    print(f"  Dislikes: {insights['dislikes']}")
    print(f"  Favorite category: {insights['favorite_category']}")
    print(f"  Least favorite category: {insights['least_favorite_category']}")
    print(f"  Most viewed category: {insights['most_viewed_category']}")
    
    # Get personalized recommendations
    recommendations = tracker.generate_personalized_recommendations(user_id)
    print(f"Personalized recommendations: {len(recommendations)} images")
    for i, rec in enumerate(recommendations):
        print(f"  {i+1}. {rec['category']}: {rec['description'][:50]}...")
    
    # Close connections
    recommender.close()
    tracker.close()
    
    print("User preference tracking tests completed successfully!")

if __name__ == "__main__":
    test_user_preference_tracking()
