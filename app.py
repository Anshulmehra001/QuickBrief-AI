import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for development
CORS(app)

# Validate required environment variables on startup
def validate_environment():
    """Validate that required environment variables are present."""
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        logger.error("GOOGLE_API_KEY environment variable is not set")
        return False
    logger.info("Environment validation successful")
    return True

@app.route('/')
def index():
    """Serve the main application page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving main page: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze earnings call transcript from provided URL.
    
    Expected JSON payload:
    {
        "url": "https://example.com/transcript"
    }
    
    Returns:
    {
        "sentiment": "string",
        "good_news": ["string"],
        "bad_news": ["string"],
        "key_promises": ["string"],
        "verdict": "string"
    }
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'url' not in data:
            return jsonify({'error': 'Please provide a URL to analyze'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'Please enter a valid URL'}), 400
        
        logger.info(f"Starting analysis for URL: {url}")
        
        # Step 1: Scrape text from URL
        try:
            text_content = scrape_text_from_url(url)
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return jsonify({'error': f'Unable to access the webpage: {str(e)}'}), 400
        
        # Step 2: Analyze text with AI
        try:
            analysis_result = analyze_text_with_ai(text_content)
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return jsonify({'error': f'Unable to analyze the content: {str(e)}'}), 500
        
        logger.info("Analysis completed successfully")
        return jsonify(analysis_result), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import google.generativeai as genai
import json

def scrape_text_from_url(url):
    """
    Extract text content from a given URL.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        str: Extracted text content
        
    Raises:
        Exception: If scraping fails for any reason
    """
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        if parsed_url.scheme not in ['http', 'https']:
            raise ValueError("URL must use HTTP or HTTPS protocol")
        
        # Configure headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make request with timeout
        logger.info(f"Scraping content from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up text - remove extra whitespace and empty lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        if len(text.strip()) < 100:
            raise ValueError("Insufficient text content found on the page")
        
        logger.info(f"Successfully extracted {len(text)} characters of text")
        return text
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while scraping {url}")
        raise Exception("Request timed out - the website took too long to respond")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while scraping {url}")
        raise Exception("Could not connect to the website - please check the URL")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while scraping {url}: {e}")
        raise Exception(f"Website returned an error: {e}")
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise Exception(str(e))
    except Exception as e:
        logger.error(f"Unexpected error while scraping {url}: {str(e)}")
        raise Exception("Failed to extract content from the website")

def analyze_text_with_ai(text):
    """
    Analyze transcript text using Google Gemini AI.
    
    Args:
        text (str): The transcript text to analyze
        
    Returns:
        dict: Structured analysis results
        
    Raises:
        Exception: If AI analysis fails for any reason
    """
    try:
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key not configured")
        
        # Configure Gemini AI
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Truncate text if too long (20,000 character limit)
        if len(text) > 20000:
            text = text[:20000]
            logger.info("Text truncated to 20,000 characters for AI processing")
        
        # Create structured prompt for consistent JSON responses
        prompt = f"""
        Analyze this earnings call transcript and provide a structured analysis in JSON format.
        
        Please analyze the following earnings call transcript and return ONLY a valid JSON object with these exact keys:
        - "sentiment": A 1-2 word summary of the overall sentiment (e.g., "Positive", "Mixed", "Cautious")
        - "good_news": An array of 3-5 positive highlights from the call
        - "bad_news": An array of 3-5 negative points or concerns mentioned
        - "key_promises": An array of 2-4 key management promises or forward-looking statements
        - "verdict": A paragraph summary for investors explaining the key takeaways
        
        Transcript text:
        {text}
        
        Return only the JSON object, no additional text or formatting:
        """
        
        logger.info("Sending text to Gemini AI for analysis...")
        
        # Generate analysis
        response = model.generate_content(prompt)
        
        if not response.text:
            raise Exception("Empty response from AI service")
        
        # Parse JSON response
        try:
            analysis_result = json.loads(response.text.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response if it contains extra text
            response_text = response.text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
                analysis_result = json.loads(json_text)
            else:
                raise Exception("Could not parse AI response as JSON")
        
        # Validate required fields
        required_fields = ['sentiment', 'good_news', 'bad_news', 'key_promises', 'verdict']
        for field in required_fields:
            if field not in analysis_result:
                raise Exception(f"AI response missing required field: {field}")
        
        logger.info("AI analysis completed successfully")
        return analysis_result
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise Exception(str(e))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise Exception("AI service returned invalid response format")
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        raise Exception("Failed to analyze transcript with AI service")

if __name__ == '__main__':
    # Validate environment on startup
    if not validate_environment():
        logger.error("Environment validation failed. Please check your configuration.")
        exit(1)
    
    # Run the application
    logger.info("Starting QuickBrief AI application...")
    app.run(debug=True, host='0.0.0.0', port=5001)