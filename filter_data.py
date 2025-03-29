import os
import pandas as pd
import json
import sqlite3
import random
import requests
from urllib.parse import urlparse
from datetime import datetime
import re

# Import process_data module
from process_data import CATEGORIES, process_csv_data

def filter_irrelevant_images(categories):
    """Filter out irrelevant images from the categorized dataset with improved keywords."""
    # Expanded relevance keywords for each category
    relevance_keywords = {
        'toilet': ['toilet', 'commode', 'wc', 'bathroom fixture', 'lavatory', 'water closet', 'flush', 'bidet'],
        'standing_shower': ['shower', 'shower door', 'shower head', 'shower stall', 'shower glass', 'shower tile', 'walk in shower', 'shower enclosure', 'rainfall shower'],
        'bathtub': ['bathtub', 'bath', 'tub', 'soaking', 'freestanding', 'clawfoot', 'jacuzzi', 'whirlpool', 'spa bath'],
        'mirror': ['mirror', 'bathroom mirror', 'vanity mirror', 'wall mirror', 'framed mirror', 'medicine cabinet'],
        'vanity': ['vanity', 'sink', 'cabinet', 'countertop', 'bathroom cabinet', 'washbasin', 'basin', 'bathroom furniture'],
        'floor_tiles': ['tile', 'floor', 'ceramic', 'porcelain', 'marble', 'pattern', 'mosaic', 'travertine', 'slate', 'limestone', 'flooring'],
        'color': ['color', 'paint', 'palette', 'scheme', 'tone', 'hue', 'bathroom color', 'wall color', 'accent', 'decor']
    }
    
    # Expanded irrelevance keywords
    irrelevance_keywords = [
        'person', 'people', 'woman', 'man', 'child', 'sofa', 'couch', 'living room', 
        'kitchen', 'bedroom', 'office', 'outdoor', 'garden', 'food', 'car', 'vehicle',
        'dog', 'cat', 'pet', 'animal', 'clothing', 'fashion', 'restaurant', 'cafe',
        'store', 'shop', 'concert', 'party', 'beach', 'mountain', 'forest'
    ]
    
    # Statistics before filtering
    before_counts = {category: len(images) for category, images in categories.items()}
    total_before = sum(before_counts.values())
    
    # Filter out irrelevant images
    filtered_categories = {}
    removed_counts = {category: 0 for category in categories}
    
    for category, images in categories.items():
        filtered_images = []
        
        for image in images:
            description = image.get('description', '').lower()
            url = image.get('url', '').lower()
            
            # Check if the image is relevant based on keywords
            is_relevant = False
            
            # Check for relevance keywords in description or URL
            for keyword in relevance_keywords[category]:
                if keyword.lower() in description or keyword.lower() in url:
                    is_relevant = True
                    break
            
            # Check for irrelevance keywords
            for keyword in irrelevance_keywords:
                if keyword.lower() in description:
                    is_relevant = False
                    break
            
            # Special case for floor_tiles: exclude images with people or furniture as main subject
            if category == 'floor_tiles' and any(kw in description for kw in ['sofa', 'person', 'people']):
                is_relevant = False
            
            # Add relevant images to filtered list
            if is_relevant:
                filtered_images.append(image)
            else:
                removed_counts[category] += 1
        
        filtered_categories[category] = filtered_images
    
    # Statistics after filtering
    after_counts = {category: len(images) for category, images in filtered_categories.items()}
    total_after = sum(after_counts.values())
    
    # Print statistics
    print("Filtering complete!")
    print(f"Total images before filtering: {total_before}")
    print(f"Total images after filtering: {total_after}")
    print(f"Total removed: {total_before - total_after} ({(total_before - total_after) / total_before * 100:.2f}%)")
    print("\nCategory statistics:")
    
    for category in categories:
        print(f"{category}: {before_counts[category]} → {after_counts[category]} " +
              f"(removed: {removed_counts[category]}, {removed_counts[category] / before_counts[category] * 100:.2f}%)")
    
    return filtered_categories
