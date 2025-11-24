// QuickBrief AI - Client-side JavaScript functionality

class QuickBriefAI {
    constructor() {
        this.form = document.getElementById('analysisForm');
        this.urlInput = document.getElementById('urlInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.analyzeText = document.getElementById('analyzeText');
        this.analyzeSpinner = document.getElementById('analyzeSpinner');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.loadingMessage = document.getElementById('loadingMessage');
        this.errorContainer = document.getElementById('errorContainer');
        this.errorMessage = document.getElementById('errorMessage');
        this.resultsContainer = document.getElementById('resultsContainer');
        
        // Result elements
        this.sentimentValue = document.getElementById('sentimentValue');
        this.goodNewsList = document.getElementById('goodNewsList');
        this.badNewsList = document.getElementById('badNewsList');
        this.promisesList = document.getElementById('promisesList');
        this.verdictText = document.getElementById('verdictText');
        
        this.isAnalyzing = false;
        this.loadingMessages = [
            'Extracting content from URL...',
            'Processing transcript text...',
            'Analyzing with AI...',
            'Generating insights...',
            'Finalizing results...'
        ];
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.form.addEventListener('submit', this.handleFormSubmit.bind(this));
        this.urlInput.addEventListener('input', this.handleInputChange.bind(this));
        
        // Initial state
        this.hideAllContainers();
    }
    
    handleFormSubmit(event) {
        event.preventDefault();
        
        if (this.isAnalyzing) {
            return;
        }
        
        const url = this.urlInput.value.trim();
        
        if (!this.validateUrl(url)) {
            this.showError('Please enter a valid URL');
            return;
        }
        
        this.startAnalysis(url);
    }
    
    handleInputChange() {
        // Clear error when user starts typing
        if (!this.errorContainer.classList.contains('d-none')) {
            this.hideError();
        }
    }
    
    validateUrl(url) {
        if (!url) {
            return false;
        }
        
        try {
            const urlObj = new URL(url);
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        } catch (e) {
            return false;
        }
    }
    
    async startAnalysis(url) {
        this.isAnalyzing = true;
        this.hideAllContainers();
        this.setLoadingState(true);
        this.startLoadingAnimation();
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            this.displayResults(data);
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError(this.getErrorMessage(error));
        } finally {
            this.setLoadingState(false);
            this.isAnalyzing = false;
        }
    }
    
    setLoadingState(loading) {
        if (loading) {
            this.analyzeBtn.disabled = true;
            this.analyzeText.textContent = 'Analyzing...';
            this.analyzeSpinner.classList.remove('d-none');
            this.loadingIndicator.classList.remove('d-none');
            this.loadingIndicator.classList.add('slide-in');
        } else {
            this.analyzeBtn.disabled = false;
            this.analyzeText.textContent = 'Analyze';
            this.analyzeSpinner.classList.add('d-none');
            this.loadingIndicator.classList.add('d-none');
            this.loadingIndicator.classList.remove('slide-in');
        }
    }
    
    startLoadingAnimation() {
        let messageIndex = 0;
        
        const updateMessage = () => {
            if (!this.isAnalyzing) return;
            
            this.loadingMessage.textContent = this.loadingMessages[messageIndex];
            messageIndex = (messageIndex + 1) % this.loadingMessages.length;
            
            setTimeout(updateMessage, 3000);
        };
        
        updateMessage();
    }
    
    displayResults(data) {
        this.hideAllContainers();
        
        // Display sentiment
        this.sentimentValue.textContent = data.sentiment || 'N/A';
        this.setSentimentColor(data.sentiment);
        
        // Display good news
        this.populateList(this.goodNewsList, data.good_news || []);
        
        // Display bad news
        this.populateList(this.badNewsList, data.bad_news || []);
        
        // Display key promises
        this.populateList(this.promisesList, data.key_promises || []);
        
        // Display verdict
        this.verdictText.textContent = data.verdict || 'No verdict available';
        
        // Show results container with animation
        this.resultsContainer.classList.remove('d-none');
        this.resultsContainer.classList.add('slide-in');
        
        // Scroll to results
        this.resultsContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    setSentimentColor(sentiment) {
        // Remove existing sentiment classes
        this.sentimentValue.classList.remove('text-success', 'text-warning', 'text-danger', 'text-info');
        
        if (!sentiment) return;
        
        const sentimentLower = sentiment.toLowerCase();
        
        if (sentimentLower.includes('positive') || sentimentLower.includes('bullish') || sentimentLower.includes('optimistic')) {
            this.sentimentValue.classList.add('text-success');
        } else if (sentimentLower.includes('negative') || sentimentLower.includes('bearish') || sentimentLower.includes('pessimistic')) {
            this.sentimentValue.classList.add('text-danger');
        } else if (sentimentLower.includes('neutral') || sentimentLower.includes('mixed')) {
            this.sentimentValue.classList.add('text-warning');
        } else {
            this.sentimentValue.classList.add('text-info');
        }
    }
    
    populateList(listElement, items) {
        listElement.innerHTML = '';
        
        if (!items || items.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No items found';
            li.classList.add('text-muted', 'fst-italic');
            listElement.appendChild(li);
            return;
        }
        
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            listElement.appendChild(li);
        });
    }
    
    showError(message) {
        this.hideAllContainers();
        this.errorMessage.textContent = message;
        this.errorContainer.classList.remove('d-none');
        this.errorContainer.classList.add('slide-in');
        
        // Scroll to error
        this.errorContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    }
    
    hideError() {
        this.errorContainer.classList.add('d-none');
        this.errorContainer.classList.remove('slide-in');
    }
    
    hideAllContainers() {
        this.errorContainer.classList.add('d-none');
        this.resultsContainer.classList.add('d-none');
        this.loadingIndicator.classList.add('d-none');
        
        // Remove animation classes
        this.errorContainer.classList.remove('slide-in');
        this.resultsContainer.classList.remove('slide-in');
        this.loadingIndicator.classList.remove('slide-in');
    }
    
    getErrorMessage(error) {
        const message = error.message || 'An unexpected error occurred';
        
        // Provide user-friendly error messages
        if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
            return 'Network error: Please check your internet connection and try again.';
        }
        
        if (message.includes('404')) {
            return 'The provided URL could not be found. Please check the URL and try again.';
        }
        
        if (message.includes('403') || message.includes('401')) {
            return 'Access denied: The website may be blocking automated requests.';
        }
        
        if (message.includes('timeout')) {
            return 'Request timeout: The analysis took too long. Please try again with a different URL.';
        }
        
        if (message.includes('API key')) {
            return 'Configuration error: Please contact support for assistance.';
        }
        
        if (message.includes('rate limit')) {
            return 'Service temporarily unavailable: Too many requests. Please try again in a few minutes.';
        }
        
        // Return the original message if no specific handling is needed
        return message;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuickBriefAI();
});

// Handle page visibility changes to pause/resume operations
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, could pause operations if needed
        console.log('Page hidden');
    } else {
        // Page is visible again
        console.log('Page visible');
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
});