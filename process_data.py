import os
import pandas as pd
import json
import sqlite3
import random
import requests
from urllib.parse import urlparse
from datetime import datetime
import re

# Define the categories we want to use
CATEGORIES = [
    'toilet', 
    'standing_shower', 
    'bathtub', 
    'mirror', 
    'vanity', 
    'floor_tiles', 
    'color'
]

def is_valid_url(url):
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_urls_from_text(text):
    """Extract URLs from text content."""
    urls = []
    lines = text.strip().split('\n')
    for line in lines:
        parts = line.strip().split()
        for part in parts:
            if is_valid_url(part):
                urls.append(part)
    return urls

def process_csv_data(shower_csv, floor_csv, text_files):
    """Process CSV files and text files to categorize images."""
    # Initialize categories dictionary
    categories = {category: [] for category in CATEGORIES}
    
    # Process bathroom_shower_images.csv
    shower_df = pd.read_csv(shower_csv)
    for _, row in shower_df.iterrows():
        # Handle missing or NaN descriptions
        description = str(row['Description']) if pd.notna(row['Description']) else ""
        
        if 'shower' in description.lower():
            categories['standing_shower'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"shower_{row['Image_ID']}"
            })
        elif 'bath' in description.lower() or 'tub' in description.lower():
            categories['bathtub'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"bath_{row['Image_ID']}"
            })
        elif 'mirror' in description.lower():
            categories['mirror'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"mirror_{row['Image_ID']}"
            })
        elif 'vanity' in description.lower():
            categories['vanity'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"vanity_{row['Image_ID']}"
            })
        elif 'toilet' in description.lower():
            categories['toilet'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"toilet_{row['Image_ID']}"
            })
    
    # Process floor_tile_images.csv
    floor_df = pd.read_csv(floor_csv)
    for _, row in floor_df.iterrows():
        # Handle missing or NaN descriptions
        description = str(row['Description']) if pd.notna(row['Description']) else ""
        
        if 'tile' in description.lower() or 'floor' in description.lower():
            categories['floor_tiles'].append({
                'url': row['URL'],
                'description': description,
                'source': row['Source'],
                'id': f"floor_{row['Image_ID']}"
            })
    
    # Process text files
    file_category_mapping = {
        'bathroom_mirror.txt': 'mirror',
        'bathroom_vanity.txt': 'vanity',
        'floortiles.txt': 'floor_tiles',
        'wall tiles.txt': 'floor_tiles',  # Wall tiles can be categorized with floor tiles
        'bathroom_color.txt': 'color',
    }
    
    for filename, content in text_files.items():
        category = file_category_mapping.get(filename)
        if category is None:
            continue
            
        urls = extract_urls_from_text(content)
        
        for i, url in enumerate(urls):
            categories[category].append({
                'url': url,
                'description': f"{category.replace('_', ' ')} image",
                'source': 'Pinterest',
                'id': f"{category}_{len(categories[category]) + i}"
            })
    
    # Print statistics
    print("Categorization complete!")
    for category, images in categories.items():
        print(f"{category}: {len(images)} images")
    
    return categories
