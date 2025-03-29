import os
import pandas as pd
import json
import sqlite3
import random
import requests
from urllib.parse import urlparse
from datetime import datetime
import re

# Import process_data and filter_data modules
from process_data import CATEGORIES
from filter_data import filter_irrelevant_images

def setup_database(filtered_categories):
    """Set up the SQLite database with initial data."""
    db_path = 'data/bathroom_images.db'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        description TEXT,
        source TEXT,
        category TEXT NOT NULL,
        popularity INTEGER DEFAULT 0,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id TEXT NOT NULL,
        image_id TEXT NOT NULL,
        rating INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, image_id),
        FOREIGN KEY (image_id) REFERENCES images(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS image_similarities (
        image_id1 TEXT NOT NULL,
        image_id2 TEXT NOT NULL,
        similarity_score REAL NOT NULL,
        PRIMARY KEY (image_id1, image_id2),
        FOREIGN KEY (image_id1) REFERENCES images(id),
        FOREIGN KEY (image_id2) REFERENCES images(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        image_id TEXT NOT NULL,
        view_time INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (session_id, user_id, image_id),
        FOREIGN KEY (image_id) REFERENCES images(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS category_preferences (
        user_id TEXT NOT NULL,
        category TEXT NOT NULL,
        preference_score REAL DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, category)
    )
    ''')
    
    # Prepare data for batch insertion
    images_data = []
    for category, images in filtered_categories.items():
        for image in images:
            images_data.append((
                image['id'],
                image['url'],
                image.get('description', ''),
                image.get('source', 'Unknown'),
                category,
                0,  # Initial popularity
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    # Batch insert
    cursor.executemany(
        'INSERT OR REPLACE INTO images (id, url, description, source, category, popularity, date_added) VALUES (?, ?, ?, ?, ?, ?, ?)',
        images_data
    )
    
    # Calculate initial similarities (simple approach: images in same category have similarity of 0.8)
    # For a notebook environment, we'll limit the number of similarity relationships to avoid performance issues
    similarities = []
    for category, images in filtered_categories.items():
        # Limit to 100 images per category for similarity calculation
        limited_images = images[:min(100, len(images))]
        for i, image1 in enumerate(limited_images):
            for j, image2 in enumerate(limited_images[i+1:i+11]):  # Only calculate for 10 nearest images
                similarities.append((image1['id'], image2['id'], 0.8))
                similarities.append((image2['id'], image1['id'], 0.8))  # Symmetrical
    
    # Batch insert similarities
    cursor.executemany(
        'INSERT OR REPLACE INTO image_similarities (image_id1, image_id2, similarity_score) VALUES (?, ?, ?)',
        similarities
    )
    
    conn.commit()
    conn.close()
    
    print(f"Database setup complete!")
    print(f"Added {len(images_data)} images to the database.")
    print(f"Calculated {len(similarities)} initial similarity relationships.")
    
    return db_path

def calculate_better_similarities_limited(filtered_categories, db_path, max_images_per_category=50):
    """Calculate better similarity relationships between images with limits to prevent performance issues."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Getting images from database...")
    # Get limited number of images per category
    images = []
    for category in CATEGORIES:
        cursor.execute('''
        SELECT id, category, description FROM images 
        WHERE category = ? 
        ORDER BY RANDOM() 
        LIMIT ?
        ''', (category, max_images_per_category))
        images.extend([dict(row) for row in cursor.fetchall()])
    
    print(f"Processing similarities for {len(images)} images...")
    # Create a dictionary for quick lookup
    image_dict = {img['id']: {'category': img['category'], 'description': img['description']} for img in images}
    
    similarities = []
    
    # Calculate similarities based on multiple factors
    for i, (id1, img1) in enumerate(image_dict.items()):
        if i % 50 == 0:
            print(f"Processing image {i}/{len(image_dict)}...")
        
        # Only compare with images in the same category to reduce computation
        same_category_ids = [id2 for id2, img2 in image_dict.items() 
                            if img2['category'] == img1['category'] and id2 != id1]
        
        # Limit the number of comparisons per image
        comparison_ids = same_category_ids[:min(20, len(same_category_ids))]
        
        for id2 in comparison_ids:
            img2 = image_dict[id2]
            similarity_score = 0.0
            
            # Same category gives base similarity
            similarity_score += 0.5
            
            # Calculate text similarity in descriptions
            desc1 = img1['description'].lower()
            desc2 = img2['description'].lower()
            
            # Count common words
            words1 = set(re.findall(r'\w+', desc1))
            words2 = set(re.findall(r'\w+', desc2))
            common_words = words1.intersection(words2)
            
            if len(words1) > 0 and len(words2) > 0:
                text_similarity = len(common_words) / max(len(words1), len(words2))
                similarity_score += 0.3 * text_similarity
            
            # Only store if similarity is significant
            if similarity_score > 0.1:  # Lower threshold to get more results
                similarities.append((id1, id2, similarity_score))
    
    print(f"Inserting {len(similarities)} similarity relationships...")
    # Batch insert or update
    cursor.executemany(
        'INSERT OR REPLACE INTO image_similarities (image_id1, image_id2, similarity_score) VALUES (?, ?, ?)',
        similarities
    )
    
    conn.commit()
    conn.close()
    
    print(f"Enhanced similarity calculation complete! Created {len(similarities)} relationships.")
    return len(similarities)
