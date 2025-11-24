#!/usr/bin/env python3
"""
Test script for QuickBrief AI complete analysis workflow.
This script tests the end-to-end functionality without requiring real API keys.
"""

import os
import sys
import json
import requests
from unittest.mock import patch, MagicMock
import tempfile
import time

# Add the current directory to Python path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_url_validation():
    """Test URL validation functionality."""
    print("Testing URL validation...")
    
    from app import scrape_text_from_url
    from urllib.parse import urlparse
    
    # Test invalid URLs
    invalid_urls = [
        "",
        "not-a-url",
        "ftp://example.com",
        "javascript:alert('test')"
    ]
    
    for url in invalid_urls:
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                print(f"✓ Correctly rejected invalid URL: {url}")
            else:
                print(f"✗ Failed to reject invalid URL: {url}")
        except Exception as e:
            print(f"✓ Correctly rejected invalid URL: {url} - {str(e)}")
    
    print("URL validation tests completed.\n")

def test_scraping_function():
    """Test the web scraping functionality with mocked responses."""
    print("Testing web scraping function...")
    
    from app import scrape_text_from_url
    
    # Mock a successful HTTP response
    mock_html = """
    <html>
        <head><title>Test Earnings Call</title></head>
        <body>
            <script>console.log('test');</script>
            <style>body { color: red; }</style>
            <h1>Q3 2024 Earnings Call Transcript</h1>
            <p>Welcome to our quarterly earnings call. We had strong performance this quarter with revenue growth of 15%.</p>
            <p>Our key metrics show positive trends across all business segments.</p>
            <p>Looking forward, we expect continued growth in the next quarter.</p>
        </body>
    </html>
    """
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        try:
            result = scrape_text_from_url("https://example.com/transcript")
            
            # Verify content extraction
            if "Q3 2024 Earnings Call Transcript" in result:
                print("✓ Successfully extracted title")
            else:
                print("✗ Failed to extract title")
            
            if "revenue growth of 15%" in result:
                print("✓ Successfully extracted content")
            else:
                print("✗ Failed to extract content")
            
            # Verify script/style removal
            if "console.log" not in result and "color: red" not in result:
                print("✓ Successfully removed script and style tags")
            else:
                print("✗ Failed to remove script/style tags")
            
            print(f"✓ Extracted {len(result)} characters of text")
            
        except Exception as e:
            print(f"✗ Scraping function failed: {str(e)}")
    
    print("Web scraping tests completed.\n")

def test_ai_analysis_function():
    """Test the AI analysis functionality with mocked responses."""
    print("Testing AI analysis function...")
    
    from app import analyze_text_with_ai
    
    # Mock AI response
    mock_ai_response = {
        "sentiment": "Positive",
        "good_news": [
            "Revenue growth of 15% this quarter",
            "Strong performance across all segments",
            "Positive trends in key metrics"
        ],
        "bad_news": [
            "Some supply chain challenges",
            "Increased competition in core markets"
        ],
        "key_promises": [
            "Continued growth expected next quarter",
            "Investment in new technology platforms"
        ],
        "verdict": "Strong quarterly performance with positive outlook for continued growth, despite some operational challenges."
    }
    
    with patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Set a mock API key
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            try:
                test_text = "This is a test earnings call transcript with positive results."
                result = analyze_text_with_ai(test_text)
                
                # Verify response structure
                required_fields = ['sentiment', 'good_news', 'bad_news', 'key_promises', 'verdict']
                for field in required_fields:
                    if field in result:
                        print(f"✓ Response contains required field: {field}")
                    else:
                        print(f"✗ Response missing required field: {field}")
                
                # Verify data types
                if isinstance(result['good_news'], list):
                    print("✓ good_news is a list")
                else:
                    print("✗ good_news is not a list")
                
                if isinstance(result['bad_news'], list):
                    print("✓ bad_news is a list")
                else:
                    print("✗ bad_news is not a list")
                
                print(f"✓ AI analysis completed successfully")
                
            except Exception as e:
                print(f"✗ AI analysis function failed: {str(e)}")
    
    print("AI analysis tests completed.\n")

def test_flask_endpoints():
    """Test Flask application endpoints."""
    print("Testing Flask application endpoints...")
    
    # Import Flask app
    from app import app
    
    # Create test client
    with app.test_client() as client:
        # Test root endpoint
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Root endpoint accessible")
            else:
                print(f"✗ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Root endpoint error: {str(e)}")
        
        # Test analyze endpoint with invalid data
        try:
            response = client.post('/analyze', json={})
            if response.status_code == 400:
                print("✓ Analyze endpoint correctly rejects empty data")
            else:
                print(f"✗ Analyze endpoint should return 400 for empty data, got: {response.status_code}")
        except Exception as e:
            print(f"✗ Analyze endpoint error: {str(e)}")
        
        # Test analyze endpoint with invalid URL
        try:
            response = client.post('/analyze', json={"url": "not-a-url"})
            if response.status_code == 400:
                print("✓ Analyze endpoint correctly rejects invalid URL")
            else:
                print(f"✗ Analyze endpoint should return 400 for invalid URL, got: {response.status_code}")
        except Exception as e:
            print(f"✗ Analyze endpoint error: {str(e)}")
    
    print("Flask endpoint tests completed.\n")

def test_error_handling():
    """Test error handling scenarios."""
    print("Testing error handling scenarios...")
    
    from app import scrape_text_from_url, analyze_text_with_ai
    
    # Test scraping timeout
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        
        try:
            scrape_text_from_url("https://example.com")
            print("✗ Should have raised timeout exception")
        except Exception as e:
            if "timed out" in str(e).lower():
                print("✓ Correctly handled timeout error")
            else:
                print(f"✗ Unexpected error message: {str(e)}")
    
    # Test scraping connection error
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        try:
            scrape_text_from_url("https://example.com")
            print("✗ Should have raised connection exception")
        except Exception as e:
            if "connect" in str(e).lower():
                print("✓ Correctly handled connection error")
            else:
                print(f"✗ Unexpected error message: {str(e)}")
    
    # Test AI analysis without API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            analyze_text_with_ai("test text")
            print("✗ Should have raised API key error")
        except Exception as e:
            if "api key" in str(e).lower():
                print("✓ Correctly handled missing API key")
            else:
                print(f"✗ Unexpected error message: {str(e)}")
    
    print("Error handling tests completed.\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("QuickBrief AI - Complete Analysis Workflow Tests")
    print("=" * 60)
    print()
    
    # Run all test functions
    test_url_validation()
    test_scraping_function()
    test_ai_analysis_function()
    test_flask_endpoints()
    test_error_handling()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()