import os
import pandas as pd
import json
import sqlite3
import random
import requests
from urllib.parse import urlparse
from datetime import datetime
import re

class RecommendationSystem:
    def __init__(self, db_path='data/bathroom_images.db'):
        """Initialize the recommendation system with database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def get_initial_recommendations(self, limit=20):
        """Get initial recommendations based on popularity."""
        self.cursor.execute('''
        SELECT * FROM images 
        ORDER BY popularity DESC, RANDOM()
        LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_recommendations_by_category(self, category, limit=20):
        """Get recommendations for a specific category."""
        self.cursor.execute('''
        SELECT * FROM images 
        WHERE category = ?
        ORDER BY popularity DESC, RANDOM()
        LIMIT ?
        ''', (category, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_similar_images(self, image_id, limit=12):
        """Get similar images based on similarity scores."""
        self.cursor.execute('''
        SELECT i.* 
        FROM images i
        JOIN image_similarities s ON i.id = s.image_id2
        WHERE s.image_id1 = ?
        ORDER BY s.similarity_score DESC, i.popularity DESC
        LIMIT ?
        ''', (image_id, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_personalized_recommendations(self, user_id, limit=20):
        """Get personalized recommendations based on user preferences."""
        # Get user's category preferences
        self.cursor.execute('''
        SELECT category, preference_score 
        FROM category_preferences
        WHERE user_id = ?
        ORDER BY preference_score DESC
        ''', (user_id,))
        
        category_prefs = {row['category']: row['preference_score'] for row in self.cursor.fetchall()}
        
        # If user has no preferences yet, return popular images
        if not category_prefs:
            return self.get_initial_recommendations(limit)
        
        # Get images from preferred categories
        recommendations = []
        total_score = sum(category_prefs.values())
        
        # Handle case where all preference scores are 0
        if total_score == 0:
            # Assign equal weight to all categories
            for category in category_prefs:
                category_limit = max(1, int(limit / len(category_prefs)))
                self.cursor.execute('''
                SELECT i.* 
                FROM images i
                LEFT JOIN user_preferences p ON i.id = p.image_id AND p.user_id = ?
                WHERE i.category = ? AND (p.rating IS NULL OR p.rating > 0)
                ORDER BY i.popularity DESC, RANDOM()
                LIMIT ?
                ''', (user_id, category, category_limit))
                
                recommendations.extend([dict(row) for row in self.cursor.fetchall()])
            return recommendations[:limit]
        
        for category, score in sorted(category_prefs.items(), key=lambda x: x[1], reverse=True):
            # Number of images to get from this category is proportional to preference score
            category_limit = max(1, int(limit * (score / total_score)))
            
            self.cursor.execute('''
            SELECT i.* 
            FROM images i
            LEFT JOIN user_preferences p ON i.id = p.image_id AND p.user_id = ?
            WHERE i.category = ? AND (p.rating IS NULL OR p.rating > 0)
            ORDER BY i.popularity DESC, RANDOM()
            LIMIT ?
            ''', (user_id, category, category_limit))
            
            recommendations.extend([dict(row) for row in self.cursor.fetchall()])
        
        # If we don't have enough recommendations, add some popular images
        if len(recommendations) < limit:
            self.cursor.execute('''
            SELECT i.* 
            FROM images i
            LEFT JOIN user_preferences p ON i.id = p.image_id AND p.user_id = ?
            WHERE p.image_id IS NULL
            ORDER BY i.popularity DESC, RANDOM()
            LIMIT ?
            ''', (user_id, limit - len(recommendations)))
            
            recommendations.extend([dict(row) for row in self.cursor.fetchall()])
        
        return recommendations[:limit]
    
    def record_user_preference(self, user_id, image_id, rating):
        """Record user preference (like/dislike) for an image."""
        # Get image category
        self.cursor.execute('SELECT category FROM images WHERE id = ?', (image_id,))
        result = self.cursor.fetchone()
        if not result:
            return False
        
        category = result['category']
        
        # Record preference
        self.cursor.execute('''
        INSERT OR REPLACE INTO user_preferences (user_id, image_id, rating, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (user_id, image_id, rating, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Update image popularity
        self.cursor.execute('''
        UPDATE images
        SET popularity = popularity + ?
        WHERE id = ?
        ''', (rating, image_id))
        
        # Update category preference
        self.cursor.execute('''
        INSERT INTO category_preferences (user_id, category, preference_score, timestamp)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, category) 
        DO UPDATE SET 
            preference_score = preference_score + ?,
            timestamp = ?
        ''', (
            user_id, category, rating, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            rating, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        self.conn.commit()
        return True
    
    def record_view_time(self, session_id, user_id, image_id, view_time):
        """Record time spent viewing an image."""
        self.cursor.execute('''
        INSERT OR REPLACE INTO user_sessions (session_id, user_id, image_id, view_time, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id, user_id, image_id, view_time, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # If view time is significant, slightly increase image popularity
        if view_time > 5:  # More than 5 seconds
            self.cursor.execute('''
            UPDATE images
            SET popularity = popularity + 0.5
            WHERE id = ?
            ''', (image_id,))
            
            # Get image category
            self.cursor.execute('SELECT category FROM images WHERE id = ?', (image_id,))
            result = self.cursor.fetchone()
            if result:
                category = result['category']
                
                # Slightly increase category preference
                self.cursor.execute('''
                INSERT INTO category_preferences (user_id, category, preference_score, timestamp)
                VALUES (?, ?, 0.2, ?)
                ON CONFLICT(user_id, category) 
                DO UPDATE SET 
                    preference_score = preference_score + 0.2,
                    timestamp = ?
                ''', (
                    user_id, category, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        
        self.conn.commit()
        return True
    
    def update_similarity_scores(self, user_id):
        """Update similarity scores based on user preferences."""
        # Get user's liked images
        self.cursor.execute('''
        SELECT image_id FROM user_preferences
        WHERE user_id = ? AND rating > 0
        ''', (user_id,))
        
        liked_images = [row['image_id'] for row in self.cursor.fetchall()]
        
        # If user hasn't liked enough images, don't update similarities
        if len(liked_images) < 2:
            return 0
        
        # Increase similarity between liked images
        updates = []
        for i, img1 in enumerate(liked_images):
            for img2 in liked_images[i+1:]:
                updates.append((0.1, img1, img2))
                updates.append((0.1, img2, img1))
        
        # Batch update
        self.cursor.executemany('''
        UPDATE image_similarities
        SET similarity_score = similarity_score + ?
        WHERE image_id1 = ? AND image_id2 = ?
        ''', updates)
        
        self.conn.commit()
        return len(updates)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
