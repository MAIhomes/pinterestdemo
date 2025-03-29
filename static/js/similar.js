// JavaScript for Similar Images page

// Global variables
let viewStartTimes = {};

// DOM elements
document.addEventListener('DOMContentLoaded', function() {
    // Load original image and similar images
    loadSimilarImages();
    
    // Add event listener for page visibility changes to track view time
    document.addEventListener('visibilitychange', handleVisibilityChange);
});

// Function to load similar images
function loadSimilarImages() {
    const originalImageContainer = document.getElementById('original-image');
    const imageGrid = document.getElementById('image-grid');
    
    // Fetch similar images from API
    fetch(`/api/similar/${imageId}`)
        .then(response => response.json())
        .then(data => {
            // Display original image
            originalImageContainer.innerHTML = '';
            const originalImageElement = createOriginalImageElement(data.original);
            originalImageContainer.appendChild(originalImageElement);
            
            // Start timing view for original image
            viewStartTimes[data.original.id] = new Date();
            
            // Display similar images
            imageGrid.innerHTML = '';
            if (data.similar.length === 0) {
                imageGrid.innerHTML = '<div class="loading">No similar images found.</div>';
            } else {
                data.similar.forEach(image => {
                    const imageCard = createImageCard(image);
                    imageGrid.appendChild(imageCard);
                    
                    // Start timing view
                    viewStartTimes[image.id] = new Date();
                });
            }
        })
        .catch(error => {
            console.error('Error loading similar images:', error);
            originalImageContainer.innerHTML = '<div class="loading">Error loading original image. Please try again.</div>';
            imageGrid.innerHTML = '<div class="loading">Error loading similar images. Please try again.</div>';
        });
}

// Function to create original image element
function createOriginalImageElement(image) {
    const container = document.createElement('div');
    container.className = 'original-image-container';
    
    // Create image element
    const img = document.createElement('img');
    img.src = image.url;
    img.alt = image.description || 'Original bathroom image';
    img.onerror = function() {
        this.src = '/static/img/placeholder.jpg';
    };
    
    // Create info section
    const infoSection = document.createElement('div');
    infoSection.className = 'original-image-info';
    
    // Create title
    const title = document.createElement('h3');
    title.textContent = image.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    infoSection.appendChild(title);
    
    // Create description
    const description = document.createElement('p');
    description.textContent = image.description || 'No description available';
    infoSection.appendChild(description);
    
    // Create source
    const source = document.createElement('p');
    source.className = 'source';
    source.textContent = `Source: ${image.source || 'Unknown'}`;
    infoSection.appendChild(source);
    
    // Create actions section
    const actionsSection = document.createElement('div');
    actionsSection.className = 'image-actions';
    
    // Create like button
    const likeBtn = document.createElement('button');
    likeBtn.className = 'btn btn-like';
    likeBtn.textContent = '❤️ Like';
    likeBtn.addEventListener('click', function() {
        likeImage(image.id, this);
    });
    actionsSection.appendChild(likeBtn);
    
    // Create dislike button
    const dislikeBtn = document.createElement('button');
    dislikeBtn.className = 'btn btn-dislike';
    dislikeBtn.textContent = '✖️ Dislike';
    dislikeBtn.addEventListener('click', function() {
        dislikeImage(image.id, this);
    });
    actionsSection.appendChild(dislikeBtn);
    
    infoSection.appendChild(actionsSection);
    
    // Assemble container
    container.appendChild(img);
    container.appendChild(infoSection);
    
    return container;
}

// Function to create an image card
function createImageCard(image) {
    const card = document.createElement('div');
    card.className = 'image-card';
    card.dataset.imageId = image.id;
    
    // Create image container
    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';
    
    // Create image element
    const img = document.createElement('img');
    img.src = image.url;
    img.alt = image.description || 'Bathroom image';
    img.onerror = function() {
        this.src = '/static/img/placeholder.jpg';
    };
    imageContainer.appendChild(img);
    
    // Create info section
    const infoSection = document.createElement('div');
    infoSection.className = 'image-info';
    
    // Create title
    const title = document.createElement('h3');
    title.textContent = image.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    infoSection.appendChild(title);
    
    // Create description
    const description = document.createElement('p');
    description.textContent = image.description || 'No description available';
    infoSection.appendChild(description);
    
    // Create actions section
    const actionsSection = document.createElement('div');
    actionsSection.className = 'image-actions';
    
    // Create like button
    const likeBtn = document.createElement('button');
    likeBtn.className = 'btn btn-like';
    likeBtn.textContent = '❤️ Like';
    likeBtn.addEventListener('click', function() {
        likeImage(image.id, this);
    });
    actionsSection.appendChild(likeBtn);
    
    // Create dislike button
    const dislikeBtn = document.createElement('button');
    dislikeBtn.className = 'btn btn-dislike';
    dislikeBtn.textContent = '✖️ Dislike';
    dislikeBtn.addEventListener('click', function() {
        dislikeImage(image.id, this);
    });
    actionsSection.appendChild(dislikeBtn);
    
    // Assemble card
    card.appendChild(imageContainer);
    card.appendChild(infoSection);
    card.appendChild(actionsSection);
    
    return card;
}

// Function to like an image
function likeImage(imageId, button) {
    fetch('/api/preference', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_id: imageId,
            rating: 1
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = '❤️ Liked';
            button.disabled = true;
            button.classList.add('liked');
            
            // Disable dislike button
            const dislikeBtn = button.parentNode.querySelector('.btn-dislike');
            if (dislikeBtn) {
                dislikeBtn.disabled = true;
            }
        }
    })
    .catch(error => {
        console.error('Error liking image:', error);
    });
}

// Function to dislike an image
function dislikeImage(imageId, button) {
    fetch('/api/preference', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_id: imageId,
            rating: -1
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = '✖️ Disliked';
            button.disabled = true;
            button.classList.add('disliked');
            
            // Disable like button
            const likeBtn = button.parentNode.querySelector('.btn-like');
            if (likeBtn) {
                likeBtn.disabled = true;
            }
        }
    })
    .catch(error => {
        console.error('Error disliking image:', error);
    });
}

// Function to record view times
function recordViewTimes() {
    const now = new Date();
    
    for (const [imageId, startTime] of Object.entries(viewStartTimes)) {
        const viewTime = Math.round((now - startTime) / 1000); // Convert to seconds
        
        if (viewTime >= 1) { // Only record if viewed for at least 1 second
            fetch('/api/view_time', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_id: imageId,
                    view_time: viewTime
                }),
            })
            .catch(error => {
                console.error('Error recording view time:', error);
            });
        }
    }
    
    // Reset view start times
    viewStartTimes = {};
}

// Function to handle visibility change (tab switching)
function handleVisibilityChange() {
    if (document.hidden) {
        // Page is hidden, record view times
        recordViewTimes();
    } else {
        // Page is visible again, start timing for visible images
        const imageCards = document.querySelectorAll('.image-card');
        const now = new Date();
        
        // Original image
        const originalImageContainer = document.getElementById('original-image');
        if (originalImageContainer) {
            const originalImageId = originalImageContainer.querySelector('.original-image-container')?.dataset.imageId;
            if (originalImageId) {
                viewStartTimes[originalImageId] = now;
            }
        }
        
        // Similar images
        imageCards.forEach(card => {
            const imageId = card.dataset.imageId;
            viewStartTimes[imageId] = now;
        });
    }
}

// Handle page unload to record final view times
window.addEventListener('beforeunload', function() {
    recordViewTimes();
});
