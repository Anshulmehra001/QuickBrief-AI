#!/usr/bin/env python3
"""
Test script for QuickBrief AI error handling scenarios.
This tests various failure modes and ensures graceful degradation.
"""

import os
import sys
import json
import requests
from unittest.mock import patch, MagicMock
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_invalid_url_handling():
    """Test handling of various invalid URL formats."""
    print("Testing invalid URL handling...")
    
    from app import app
    
    invalid_urls = [
        "",
        "not-a-url",
        "ftp://example.com/file",
        "javascript:alert('xss')",
        "file:///etc/passwd",
        "http://",
        "https://",
        "   ",
        None
    ]
    
    with app.test_client() as client:
        for url in invalid_urls:
            try:
                payload = {"url": url} if url is not None else {}
                response = client.post('/analyze', json=payload)
                
                if response.status_code == 400:
                    error_data = response.get_json()
                    if 'error' in error_data:
                        print(f"✓ Correctly rejected invalid URL: {url}")
                    else:
                        print(f"✗ Missing error message for URL: {url}")
                else:
                    print(f"✗ Wrong status code for URL {url}: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ Exception handling URL {url}: {str(e)}")
    
    print("Invalid URL handling tests completed.\n")

def test_network_failure_scenarios():
    """Test various network failure scenarios."""
    print("Testing network failure scenarios...")
    
    from app import app, scrape_text_from_url
    
    # Test timeout scenarios
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/timeout"})
            
            if response.status_code == 400:
                error_data = response.get_json()
                if 'timed out' in error_data.get('error', '').lower():
                    print("✓ Correctly handled timeout error")
                else:
                    print(f"✗ Unexpected timeout error message: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for timeout: {response.status_code}")
    
    # Test connection errors
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://unreachable.example.com"})
            
            if response.status_code == 400:
                error_data = response.get_json()
                if 'connect' in error_data.get('error', '').lower():
                    print("✓ Correctly handled connection error")
                else:
                    print(f"✗ Unexpected connection error message: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for connection error: {response.status_code}")
    
    # Test HTTP errors (404, 403, 500)
    http_errors = [
        (404, "Not Found"),
        (403, "Forbidden"), 
        (500, "Internal Server Error")
    ]
    
    for status_code, reason in http_errors:
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"{status_code} {reason}")
            mock_get.return_value = mock_response
            
            with app.test_client() as client:
                response = client.post('/analyze', json={"url": f"https://example.com/{status_code}"})
                
                if response.status_code == 400:
                    error_data = response.get_json()
                    if 'error' in error_data.get('error', '').lower():
                        print(f"✓ Correctly handled HTTP {status_code} error")
                    else:
                        print(f"✗ Unexpected HTTP {status_code} error message: {error_data.get('error')}")
                else:
                    print(f"✗ Wrong status code for HTTP {status_code}: {response.status_code}")
    
    print("Network failure tests completed.\n")

def test_content_extraction_failures():
    """Test scenarios where content extraction fails."""
    print("Testing content extraction failures...")
    
    from app import app
    
    # Test empty content
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"<html><body></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/empty"})
            
            if response.status_code == 400:
                error_data = response.get_json()
                if 'insufficient' in error_data.get('error', '').lower():
                    print("✓ Correctly handled insufficient content")
                else:
                    print(f"✗ Unexpected empty content error: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for empty content: {response.status_code}")
    
    # Test malformed HTML
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"<html><body><div>Some text but not enough for analysis</div></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/short"})
            
            if response.status_code == 400:
                print("✓ Correctly handled insufficient content length")
            else:
                print(f"✗ Wrong status code for short content: {response.status_code}")
    
    print("Content extraction failure tests completed.\n")

def test_ai_service_failures():
    """Test AI service failure scenarios."""
    print("Testing AI service failures...")
    
    from app import app
    
    # Mock successful scraping but AI failure
    mock_html = "<html><body>" + "This is a test earnings call transcript. " * 20 + "</body></html>"
    
    # Test missing API key
    with patch('requests.get') as mock_get, \
         patch.dict(os.environ, {}, clear=True):
        
        mock_response = MagicMock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/transcript"})
            
            if response.status_code == 500:
                error_data = response.get_json()
                if 'api key' in error_data.get('error', '').lower():
                    print("✓ Correctly handled missing API key")
                else:
                    print(f"✗ Unexpected API key error: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for missing API key: {response.status_code}")
    
    # Test AI service timeout/error
    with patch('requests.get') as mock_get, \
         patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
        
        mock_response = MagicMock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock AI service failure
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("AI service unavailable")
        mock_model_class.return_value = mock_model
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/transcript"})
            
            if response.status_code == 500:
                error_data = response.get_json()
                if 'analysis failed' in error_data.get('error', '').lower():
                    print("✓ Correctly handled AI service failure")
                else:
                    print(f"✗ Unexpected AI service error: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for AI service failure: {response.status_code}")
    
    # Test invalid AI response format
    with patch('requests.get') as mock_get, \
         patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
        
        mock_response = MagicMock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock invalid AI response
        mock_model = MagicMock()
        mock_ai_response = MagicMock()
        mock_ai_response.text = "This is not valid JSON"
        mock_model.generate_content.return_value = mock_ai_response
        mock_model_class.return_value = mock_model
        
        with app.test_client() as client:
            response = client.post('/analyze', json={"url": "https://example.com/transcript"})
            
            if response.status_code == 500:
                error_data = response.get_json()
                if 'analysis failed' in error_data.get('error', '').lower():
                    print("✓ Correctly handled invalid AI response")
                else:
                    print(f"✗ Unexpected invalid response error: {error_data.get('error')}")
            else:
                print(f"✗ Wrong status code for invalid AI response: {response.status_code}")
    
    print("AI service failure tests completed.\n")

def test_request_validation():
    """Test request validation and malformed requests."""
    print("Testing request validation...")
    
    from app import app
    
    with app.test_client() as client:
        # Test non-JSON request
        response = client.post('/analyze', data="not json")
        if response.status_code == 400:
            print("✓ Correctly rejected non-JSON request")
        else:
            print(f"✗ Wrong status code for non-JSON: {response.status_code}")
        
        # Test empty JSON
        response = client.post('/analyze', json={})
        if response.status_code == 400:
            print("✓ Correctly rejected empty JSON")
        else:
            print(f"✗ Wrong status code for empty JSON: {response.status_code}")
        
        # Test missing URL field
        response = client.post('/analyze', json={"not_url": "value"})
        if response.status_code == 400:
            print("✓ Correctly rejected missing URL field")
        else:
            print(f"✗ Wrong status code for missing URL: {response.status_code}")
        
        # Test empty URL value
        response = client.post('/analyze', json={"url": ""})
        if response.status_code == 400:
            print("✓ Correctly rejected empty URL value")
        else:
            print(f"✗ Wrong status code for empty URL value: {response.status_code}")
        
        # Test whitespace-only URL
        response = client.post('/analyze', json={"url": "   "})
        if response.status_code == 400:
            print("✓ Correctly rejected whitespace-only URL")
        else:
            print(f"✗ Wrong status code for whitespace URL: {response.status_code}")
    
    print("Request validation tests completed.\n")

def test_error_message_quality():
    """Test that error messages are user-friendly and informative."""
    print("Testing error message quality...")
    
    from app import app
    
    test_cases = [
        ({"url": "not-a-url"}, "should mention invalid URL format"),
        ({}, "should mention missing URL"),
        ({"url": ""}, "should mention empty URL"),
    ]
    
    with app.test_client() as client:
        for payload, expectation in test_cases:
            response = client.post('/analyze', json=payload)
            
            if response.status_code == 400:
                error_data = response.get_json()
                error_msg = error_data.get('error', '').lower()
                
                # Check that error message is informative
                if len(error_msg) > 10 and ('please' in error_msg or 'unable' in error_msg):
                    print(f"✓ Error message is informative: {expectation}")
                else:
                    print(f"✗ Error message could be improved: {error_msg}")
            else:
                print(f"✗ Expected 400 status for {payload}")
    
    print("Error message quality tests completed.\n")

def test_logging_functionality():
    """Test that errors are properly logged."""
    print("Testing error logging functionality...")
    
    # This test verifies that the logging statements are in place
    # In a real scenario, you'd capture log output and verify content
    
    from app import logger
    
    # Verify logger is configured
    if logger.level <= 20:  # INFO level or lower
        print("✓ Logger is configured for INFO level")
    else:
        print("✗ Logger level too high, may miss important logs")
    
    # Test that logger has handlers
    if logger.handlers or logger.parent.handlers:
        print("✓ Logger has handlers configured")
    else:
        print("✗ Logger has no handlers")
    
    print("Error logging tests completed.\n")

def main():
    """Run all error handling tests."""
    print("=" * 70)
    print("QuickBrief AI - Error Handling Scenario Tests")
    print("=" * 70)
    print()
    
    # Run all test functions
    test_invalid_url_handling()
    test_network_failure_scenarios()
    test_content_extraction_failures()
    test_ai_service_failures()
    test_request_validation()
    test_error_message_quality()
    test_logging_functionality()
    
    print("=" * 70)
    print("All error handling tests completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()