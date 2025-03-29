from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import random
import sqlite3
from datetime import datetime

from process_data import CATEGORIES, process_csv_data
from filter_data import filter_irrelevant_images
from setup_database import setup_database, calculate_better_similarities_limited
from recommendation_system import RecommendationSystem
from user_preferences import UserPreferenceTracker

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables
recommender = None
db_path = 'data/bathroom_images.db'

@app.route('/')
def index():
    """Render the home page."""
    # Create a session ID if not exists
    if 'user_id' not in session:
        session['user_id'] = f"user_{random.randint(1000, 9999)}"
    if 'session_id' not in session:
        session['session_id'] = f"session_{random.randint(1000, 9999)}"
    
    return render_template('index.html', categories=CATEGORIES)

@app.route('/api/images')
def get_images():
    """API endpoint to get images."""
    category = request.args.get('category', 'all')
    limit = int(request.args.get('limit', 12))
    
    global recommender
    if recommender is None:
        recommender = RecommendationSystem(db_path)
    
    if category == 'all':
        images = recommender.get_initial_recommendations(limit)
    elif category == 'for-you':
        images = recommender.get_personalized_recommendations(session['user_id'], limit)
    else:
        images = recommender.get_recommendations_by_category(category, limit)
    
    return jsonify(images)

@app.route('/api/similar/<image_id>')
def get_similar(image_id):
    """API endpoint to get similar images."""
    limit = int(request.args.get('limit', 12))
    
    global recommender
    if recommender is None:
        recommender = RecommendationSystem(db_path)
    
    images = recommender.get_similar_images(image_id, limit)
    
    # Get the original image
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images WHERE id = ?', (image_id,))
    original_image = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({
        'original': original_image,
        'similar': images
    })

@app.route('/api/preference', methods=['POST'])
def record_preference():
    """API endpoint to record user preference."""
    data = request.json
    image_id = data.get('image_id')
    rating = data.get('rating')  # 1 for like, -1 for dislike
    
    if not image_id or rating not in [1, -1]:
        return jsonify({'success': False, 'error': 'Invalid parameters'})
    
    global recommender
    if recommender is None:
        recommender = RecommendationSystem(db_path)
    
    success = recommender.record_user_preference(session['user_id'], image_id, rating)
    
    # Update similarity scores
    recommender.update_similarity_scores(session['user_id'])
    
    return jsonify({'success': success})

@app.route('/api/view_time', methods=['POST'])
def record_view_time():
    """API endpoint to record view time."""
    data = request.json
    image_id = data.get('image_id')
    view_time = data.get('view_time')  # in seconds
    
    if not image_id or not view_time:
        return jsonify({'success': False, 'error': 'Invalid parameters'})
    
    global recommender
    if recommender is None:
        recommender = RecommendationSystem(db_path)
    
    success = recommender.record_view_time(
        session['session_id'], 
        session['user_id'], 
        image_id, 
        view_time
    )
    
    return jsonify({'success': success})

@app.route('/similar/<image_id>')
def similar_page(image_id):
    """Render the similar images page."""
    return render_template('similar.html', image_id=image_id)

@app.route('/for-you')
def for_you_page():
    """Render the personalized recommendations page."""
    return render_template('index.html', category='for-you')

def run_enhanced_bathroom_recommender(shower_csv_path, floor_csv_path, text_files_dict):
    """Run the enhanced bathroom image recommendation system."""
    print("Starting Enhanced Bathroom Image Recommendation System...")
    
    # Process data
    print("\n1. Processing and categorizing images...")
    categories = process_csv_data(shower_csv_path, floor_csv_path, text_files_dict)
    
    # Filter images with improved filtering
    print("\n2. Filtering irrelevant images with enhanced keywords...")
    filtered_categories = filter_irrelevant_images(categories)
    
    # Setup database
    print("\n3. Setting up database...")
    global db_path
    db_path = setup_database(filtered_categories)
    
    # Calculate better similarities with limits
    print("\n4. Calculating enhanced image similarities (limited version)...")
    calculate_better_similarities_limited(filtered_categories, db_path, max_images_per_category=50)
    
    # Create global recommender
    global recommender
    recommender = RecommendationSystem(db_path)
    
    print("\n5. Starting web server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    print("\nEnhanced Bathroom Image Recommendation System is ready!")
    print("Access the application at http://localhost:5000")

if __name__ == '__main__':
    # This code will run when the script is executed directly
    # For testing purposes, you can add sample data loading here
    app.run(host='0.0.0.0', port=5000, debug=True)
