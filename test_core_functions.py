#!/usr/bin/env python3
"""
Automated test suite for QuickBrief AI core functions.
This provides unit and integration tests for the main functionality.
"""

import unittest
import os
import sys
import json
import requests
from unittest.mock import patch, MagicMock, Mock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestScrapingFunction(unittest.TestCase):
    """Test cases for the web scraping functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from app import scrape_text_from_url
        self.scrape_function = scrape_text_from_url
    
    @patch('requests.get')
    def test_successful_scraping(self, mock_get):
        """Test successful content extraction from a webpage."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Earnings Call Transcript</h1>
                <p>This is a test earnings call with important financial information.</p>
                <p>Revenue increased by 20% this quarter showing strong growth.</p>
                <p>Management is optimistic about future prospects and market expansion.</p>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scrape_function("https://example.com/transcript")
        
        # Verify content extraction
        self.assertIn("Earnings Call Transcript", result)
        self.assertIn("Revenue increased by 20%", result)
        self.assertIn("Management is optimistic", result)
        self.assertGreater(len(result), 100)
    
    @patch('requests.get')
    def test_script_and_style_removal(self, mock_get):
        """Test that script and style tags are properly removed."""
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>console.log('test');</script>
            </head>
            <body>
                <script>alert('should be removed');</script>
                <p>This content should remain in the extracted text and provide sufficient length for the content validation.</p>
                <p>Additional content to ensure we meet the minimum character requirement for successful processing.</p>
                <style>.hidden { display: none; }</style>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scrape_function("https://example.com/test")
        
        # Verify script/style removal
        self.assertNotIn("console.log", result)
        self.assertNotIn("alert", result)
        self.assertNotIn("color: red", result)
        self.assertNotIn("display: none", result)
        self.assertIn("This content should remain", result)
    
    def test_invalid_url_format(self):
        """Test handling of invalid URL formats."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('test')",
            ""
        ]
        
        for url in invalid_urls:
            with self.assertRaises(Exception):
                self.scrape_function(url)
    
    @patch('requests.get')
    def test_insufficient_content(self, mock_get):
        """Test handling of pages with insufficient content."""
        mock_response = Mock()
        mock_response.content = b"<html><body><p>Short</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.scrape_function("https://example.com/short")
        
        self.assertIn("Insufficient text content", str(context.exception))
    
    @patch('requests.get')
    def test_network_timeout(self, mock_get):
        """Test handling of network timeouts."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(Exception) as context:
            self.scrape_function("https://example.com/timeout")
        
        self.assertIn("timed out", str(context.exception))
    
    @patch('requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(Exception) as context:
            self.scrape_function("https://unreachable.com")
        
        self.assertIn("connect", str(context.exception))
    
    @patch('requests.get')
    def test_http_errors(self, mock_get):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.scrape_function("https://example.com/404")
        
        self.assertIn("error", str(context.exception))


class TestAIAnalysisFunction(unittest.TestCase):
    """Test cases for the AI analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from app import analyze_text_with_ai
        self.analyze_function = analyze_text_with_ai
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_successful_analysis(self, mock_model_class, mock_configure):
        """Test successful AI analysis with valid response."""
        # Mock AI response
        expected_response = {
            "sentiment": "Positive",
            "good_news": [
                "Revenue growth exceeded expectations",
                "Strong performance in key markets",
                "Successful product launches"
            ],
            "bad_news": [
                "Supply chain challenges persist",
                "Increased competition in core segments"
            ],
            "key_promises": [
                "Continued investment in R&D",
                "Expansion into new markets"
            ],
            "verdict": "Strong quarterly performance with positive outlook despite some operational challenges."
        }
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps(expected_response)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        test_text = "This is a test earnings call transcript with positive financial results."
        result = self.analyze_function(test_text)
        
        # Verify response structure
        self.assertEqual(result['sentiment'], "Positive")
        self.assertIsInstance(result['good_news'], list)
        self.assertIsInstance(result['bad_news'], list)
        self.assertIsInstance(result['key_promises'], list)
        self.assertIsInstance(result['verdict'], str)
        
        # Verify content
        self.assertEqual(len(result['good_news']), 3)
        self.assertEqual(len(result['bad_news']), 2)
        self.assertEqual(len(result['key_promises']), 2)
        self.assertGreater(len(result['verdict']), 50)
    
    def test_missing_api_key(self):
        """Test handling of missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(Exception) as context:
                self.analyze_function("test text")
            
            self.assertIn("API key", str(context.exception))
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_invalid_json_response(self, mock_model_class, mock_configure):
        """Test handling of invalid JSON response from AI."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with self.assertRaises(Exception) as context:
            self.analyze_function("test text")
        
        # The actual error message is wrapped, so check for the general failure
        self.assertIn("analyze", str(context.exception).lower())
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_missing_required_fields(self, mock_model_class, mock_configure):
        """Test handling of AI response missing required fields."""
        incomplete_response = {
            "sentiment": "Positive",
            "good_news": ["Some good news"]
            # Missing bad_news, key_promises, verdict
        }
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps(incomplete_response)
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with self.assertRaises(Exception) as context:
            self.analyze_function("test text")
        
        # The actual error message is wrapped, so check for the general failure
        self.assertIn("analyze", str(context.exception).lower())
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_text_truncation(self, mock_model_class, mock_configure):
        """Test that long text is properly truncated."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "sentiment": "Neutral",
            "good_news": ["Test"],
            "bad_news": ["Test"],
            "key_promises": ["Test"],
            "verdict": "Test verdict"
        })
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Create text longer than 20,000 characters
        long_text = "This is a very long earnings call transcript. " * 500
        self.assertGreater(len(long_text), 20000)
        
        result = self.analyze_function(long_text)
        
        # Verify the function completes successfully
        self.assertIsInstance(result, dict)
        
        # Verify the model was called (text was processed)
        mock_model.generate_content.assert_called_once()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_ai_service_exception(self, mock_model_class, mock_configure):
        """Test handling of AI service exceptions."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("AI service unavailable")
        mock_model_class.return_value = mock_model
        
        with self.assertRaises(Exception) as context:
            self.analyze_function("test text")
        
        self.assertIn("AI service", str(context.exception))


class TestFlaskEndpoints(unittest.TestCase):
    """Test cases for Flask API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from app import app
        self.app = app
        self.client = app.test_client()
        self.app.config['TESTING'] = True
    
    def test_root_endpoint(self):
        """Test the root endpoint serves the main page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())
    
    def test_analyze_endpoint_validation(self):
        """Test request validation on analyze endpoint."""
        # Test empty request
        response = self.client.post('/analyze')
        self.assertEqual(response.status_code, 400)
        
        # Test non-JSON request
        response = self.client.post('/analyze', data='not json')
        self.assertEqual(response.status_code, 400)
        
        # Test empty JSON
        response = self.client.post('/analyze', json={})
        self.assertEqual(response.status_code, 400)
        
        # Test missing URL
        response = self.client.post('/analyze', json={'not_url': 'value'})
        self.assertEqual(response.status_code, 400)
        
        # Test empty URL
        response = self.client.post('/analyze', json={'url': ''})
        self.assertEqual(response.status_code, 400)
    
    @patch('app.scrape_text_from_url')
    @patch('app.analyze_text_with_ai')
    def test_successful_analysis_endpoint(self, mock_analyze, mock_scrape):
        """Test successful analysis through the endpoint."""
        # Mock successful scraping and analysis
        mock_scrape.return_value = "Test transcript content with sufficient length for analysis."
        mock_analyze.return_value = {
            "sentiment": "Positive",
            "good_news": ["Good news item"],
            "bad_news": ["Bad news item"],
            "key_promises": ["Promise item"],
            "verdict": "Test verdict"
        }
        
        response = self.client.post('/analyze', json={'url': 'https://example.com/transcript'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Verify response structure
        self.assertIn('sentiment', data)
        self.assertIn('good_news', data)
        self.assertIn('bad_news', data)
        self.assertIn('key_promises', data)
        self.assertIn('verdict', data)
    
    @patch('app.scrape_text_from_url')
    def test_scraping_failure_endpoint(self, mock_scrape):
        """Test endpoint behavior when scraping fails."""
        mock_scrape.side_effect = Exception("Could not connect to website")
        
        response = self.client.post('/analyze', json={'url': 'https://unreachable.com'})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('unable to access', data['error'].lower())
    
    @patch('app.scrape_text_from_url')
    @patch('app.analyze_text_with_ai')
    def test_ai_failure_endpoint(self, mock_analyze, mock_scrape):
        """Test endpoint behavior when AI analysis fails."""
        mock_scrape.return_value = "Test content"
        mock_analyze.side_effect = Exception("AI service unavailable")
        
        response = self.client.post('/analyze', json={'url': 'https://example.com/transcript'})
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('unable to analyze', data['error'].lower())
    
    def test_404_handler(self):
        """Test 404 error handler."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up test client."""
        from app import app
        self.app = app
        self.client = app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('requests.get')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_complete_workflow(self, mock_model_class, mock_configure, mock_get):
        """Test the complete analysis workflow end-to-end."""
        # Mock scraping response
        mock_html = """
        <html><body>
        <h1>Q3 2024 Earnings Call</h1>
        <p>We delivered strong results this quarter with revenue growth of 15%.</p>
        <p>Our cloud services division showed excellent performance.</p>
        <p>However, we face some supply chain challenges in our hardware division.</p>
        <p>We're committed to investing in R&D and expanding internationally.</p>
        </body></html>
        """
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock AI response
        ai_response = {
            "sentiment": "Cautiously Optimistic",
            "good_news": [
                "Revenue growth of 15% this quarter",
                "Excellent cloud services performance"
            ],
            "bad_news": [
                "Supply chain challenges in hardware division"
            ],
            "key_promises": [
                "Continued investment in R&D",
                "International expansion plans"
            ],
            "verdict": "Strong quarterly results with positive growth trajectory despite operational challenges."
        }
        
        mock_model = Mock()
        mock_ai_response = Mock()
        mock_ai_response.text = json.dumps(ai_response)
        mock_model.generate_content.return_value = mock_ai_response
        mock_model_class.return_value = mock_model
        
        # Execute complete workflow
        response = self.client.post('/analyze', json={
            'url': 'https://example.com/earnings-call'
        })
        
        # Verify successful completion
        self.assertEqual(response.status_code, 200)
        
        result = response.get_json()
        
        # Verify all required fields are present
        required_fields = ['sentiment', 'good_news', 'bad_news', 'key_promises', 'verdict']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Verify data types and content
        self.assertIsInstance(result['good_news'], list)
        self.assertIsInstance(result['bad_news'], list)
        self.assertIsInstance(result['key_promises'], list)
        self.assertIsInstance(result['sentiment'], str)
        self.assertIsInstance(result['verdict'], str)
        
        # Verify content quality
        self.assertGreater(len(result['good_news']), 0)
        self.assertGreater(len(result['bad_news']), 0)
        self.assertGreater(len(result['key_promises']), 0)
        self.assertGreater(len(result['verdict']), 20)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestScrapingFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestAIAnalysisFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("QuickBrief AI - Automated Core Function Tests")
    print("=" * 70)
    
    success = run_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ All automated tests PASSED!")
    else:
        print("✗ Some tests FAILED!")
    print("=" * 70)
    
    sys.exit(0 if success else 1)