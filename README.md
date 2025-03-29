# Bathroom Image Recommendation System

This system processes bathroom images to categorize them, filter irrelevant content, and provide personalized recommendations based on user preferences in a Pinterest-style interface.

## Features

- **Image categorization** for bathroom fixtures (toilet, shower, bathtub, mirror, vanity, floor tiles, color)
- **Intelligent filtering** to remove irrelevant images using keyword analysis
- **Similarity calculation** to find visually and contextually related images
- **User preference tracking** that learns from likes, dislikes, and viewing time
- **Personalized recommendations** based on interaction history
- **Pinterest-style masonry layout** for intuitive browsing experience

## Installation

Clone this repository or download the Python script.

Install required dependencies:

```bash
pip install pandas flask ipywidgets pillow requests sqlite3
```

## Usage

### Basic usage with app.py (Web Application):

```bash
python app.py
```

This will process the data, set up the database, and start a web server at http://localhost:5000.

### Basic usage in Jupyter Notebook:

```python
# Run the notebook cells in sequence
# The final cell launches the interactive UI
from app import run_enhanced_bathroom_recommender
ui = run_enhanced_bathroom_recommender(shower_csv_path, floor_csv_path, text_files)
```

## Parameters

- `shower_csv_path`: Path to CSV file with shower image data (required)
- `floor_csv_path`: Path to CSV file with floor tile image data (required)
- `text_files`: Dictionary of text files containing image URLs by category (required)
- `max_images_per_category`: Maximum images to process per category (default: 50)
- `similarity_threshold`: Minimum similarity score for "more like this" (default: 0.1)

## Example with All Parameters

```python
ui = run_enhanced_bathroom_recommender(
  shower_csv_path='bathroom_shower_images.csv',
  floor_csv_path='floor_tile_images.csv',
  text_files=text_files,
  max_images_per_category=100,
  similarity_threshold=0.2
)
```

## Model Components

### Data Processing Components

- `process_csv_data`: Processes CSV files and text files to categorize images
- `filter_irrelevant_images`: Filters out irrelevant images using keyword analysis
- `setup_database`: Sets up SQLite database with tables for images, preferences, and similarities

### Recommendation Components

- `RecommendationSystem`: Core class for generating recommendations
- `get_initial_recommendations`: Provides popularity-based recommendations
- `get_recommendations_by_category`: Filters recommendations by category
- `get_similar_images`: Finds similar images based on similarity scores
- `get_personalized_recommendations`: Generates user-specific recommendations

### User Interface Components

- `BathroomRecommenderUI`: Creates interactive UI with ipywidgets
- `display_images`: Renders images in a masonry grid layout
- `like_image`/`dislike_image`: Handles user preference inputs
- `show_similar`: Displays similar images to a selected image

## Outputs

The system provides an interactive UI with:

- Category navigation buttons
- Image grid with like/dislike buttons
- "More like this" functionality
- Personalized "For You" page
- Load more button for continuous browsing

## Performance Optimization

For large image datasets, the system includes optimized similarity calculation:

```python
calculate_better_similarities_limited(
  filtered_categories, 
  db_path, 
  max_images_per_category=50
)
```

This limits the number of comparisons to prevent performance issues with large datasets.

## Extending the System

You can extend the system by:

- Adding more image sources to expand the collection
- Implementing image feature extraction for visual similarity
- Enhancing filtering keywords for better relevance
- Adding clustering algorithms for improved categorization
- Implementing image embedding models for better similarity calculation

## Limitations

- Similarity calculation is primarily text-based, not visual
- Performance may degrade with very large image collections
- Filtering accuracy depends on image descriptions
- UI is optimized for Jupyter Notebook environment

## Example Usage

This example shows how to use the bathroom recommendation system with sample data.

### Step 1: Install Dependencies

First, install all required dependencies:

```bash
pip install pandas flask ipywidgets pillow requests
```

### Step 2: Prepare Your Data Files

Organize your data files:
- CSV files with image metadata
- Text files with image URLs by category

### Step 3: Load Text Files

```python
text_files = {}

with open('bathroom_mirror.txt', 'r') as f:
    text_files['bathroom_mirror.txt'] = f.read()

with open('bathroom_vanity.txt', 'r') as f:
    text_files['bathroom_vanity.txt'] = f.read()

# Add more text files as needed
```

### Step 4: Run the System

```python
# Option 1: Run as web application
python app.py

# Option 2: Run in Jupyter Notebook
from app import run_enhanced_bathroom_recommender
shower_csv_path = 'bathroom_shower_images.csv'
floor_csv_path = 'floor_tile_images.csv'
ui = run_enhanced_bathroom_recommender(shower_csv_path, floor_csv_path, text_files)
```

### Step 5: Interact with the UI

- Browse categories using the navigation buttons
- Like or dislike images to train the system
- Click "More like this" to find similar designs
- Visit "For You" to see personalized recommendations

## Tips for Better Results

- **Data Quality**: Ensure image descriptions are detailed and accurate
- **Filtering Keywords**: Adjust relevance and irrelevance keywords for your specific dataset
- **Similarity Threshold**: Lower the threshold for more "more like this" results
- **Image Limits**: Adjust `max_images_per_category` based on your system's performance
- **User Interaction**: The system improves with more user interaction data

## Database Information

The database file (`data/bathroom_images.db`) is not included in the repository because it's generated automatically when you run the code. It's unique to each device since it takes user interactions and installations into account.

## License

Open source for personal and research use.
