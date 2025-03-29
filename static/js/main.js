// Main JavaScript for Bathroom Design Inspiration

// Global variables
let currentCategory = 'all';
let currentPage = 1;
let imagesPerPage = 12;
let viewStartTimes = {};

// DOM elements
document.addEventListener('DOMContentLoaded', function() {
    // Get current category from URL path
    const path = window.location.pathname.substring(1);
    if (path === 'for-you') {
        currentCategory = 'for-you';
    } else if (path && path !== '/') {
        currentCategory = path;
    }
    
    // Highlight active category
    const categoryLinks = document.querySelectorAll('.category-btn');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const category = this.getAttribute('href').substring(1) || 'all';
            navigateToCategory(category);
        });
        
        // Set active class based on current category
        const linkCategory = link.getAttribute('href').substring(1) || 'all';
        if (linkCategory === currentCategory) {
            link.classList.add('active');
        }
    });
    
    // Load initial images
    loadImages();
    
    // Add event listener for load more button
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            currentPage++;
            loadImages(true);
        });
    }
    
    // Add event listener for page visibility changes to track view time
    document.addEventListener('visibilitychange', handleVisibilityChange);
});

// Function to navigate to a category
function navigateToCategory(category) {
    // Record view times for current images
    recordViewTimes();
    
    // Update URL without reloading page
    const url = category === 'all' ? '/' : `/${category}`;
    history.pushState({category: category}, '', url);
    
    // Update current category and reset page
    currentCategory = category;
    currentPage = 1;
    
    // Update active class on category buttons
    const categoryLinks = document.querySelectorAll('.category-btn');
    categoryLinks.forEach(link => {
        const linkCategory = link.getAttribute('href').substring(1) || 'all';
        if (linkCategory === category) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Load images for the new category
    loadImages();
}

// Function to load images
function loadImages(append = false) {
    const imageGrid = document.getElementById('image-grid');
    
    // Show loading indicator if not appending
    if (!append) {
        imageGrid.innerHTML = '<div class="loading">Loading images...</div>';
        viewStartTimes = {}; // Reset view start times
    }
    
    // Fetch images from API
    fetch(`/api/images?category=${currentCategory}&limit=${imagesPerPage}&page=${currentPage}`)
        .then(response => response.json())
        .then(images => {
            // Remove loading indicator if not appending
            if (!append) {
                imageGrid.innerHTML = '';
            } else {
                // Remove loading indicator if it exists
                const loadingEl = imageGrid.querySelector('.loading');
                if (loadingEl) {
                    loadingEl.remove();
                }
            }
            
            // Display images
            if (images.length === 0) {
                if (!append) {
                    imageGrid.innerHTML = '<div class="loading">No images found for this category.</div>';
                }
                // Hide load more button if no more images
                document.getElementById('load-more-btn').style.display = 'none';
            } else {
                // Show load more button
                document.getElementById('load-more-btn').style.display = 'block';
                
                // Add images to grid
                images.forEach(image => {
                    const imageCard = createImageCard(image);
                    imageGrid.appendChild(imageCard);
                    
                    // Start timing view
                    viewStartTimes[image.id] = new Date();
                });
            }
        })
        .catch(error => {
            console.error('Error loading images:', error);
            imageGrid.innerHTML = '<div class="loading">Error loading images. Please try again.</div>';
        });
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
    
    // Create similar button
    const similarBtn = document.createElement('button');
    similarBtn.className = 'btn btn-similar';
    similarBtn.textContent = 'More like this';
    similarBtn.addEventListener('click', function() {
        window.location.href = `/similar/${image.id}`;
    });
    actionsSection.appendChild(similarBtn);
    
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
