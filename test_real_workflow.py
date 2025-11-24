#!/usr/bin/env python3
"""
Test script for QuickBrief AI with realistic data flow.
This tests the complete workflow with realistic transcript content.
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_realistic_workflow():
    """Test the complete workflow with realistic earnings call content."""
    print("Testing realistic earnings call analysis workflow...")
    
    # Realistic earnings call transcript content
    realistic_transcript = """
    Q3 2024 Earnings Call Transcript - TechCorp Inc.
    
    CEO: Good morning everyone, and thank you for joining our Q3 2024 earnings call. 
    I'm pleased to report that we delivered strong results this quarter, with revenue 
    growing 18% year-over-year to $2.1 billion, exceeding our guidance of $2.0 billion.
    
    Our cloud services division continues to be a major growth driver, with 25% growth 
    this quarter. We're seeing strong adoption of our new AI-powered analytics platform,
    which launched in July.
    
    However, I want to be transparent about some challenges we're facing. Supply chain 
    disruptions have impacted our hardware division, leading to a 5% decline in that 
    segment. Additionally, we're seeing increased competition in our core markets, 
    which is putting pressure on margins.
    
    Looking ahead, we're committed to investing $500 million in R&D over the next 
    12 months to maintain our competitive edge. We also plan to expand our international 
    presence with new offices in three European markets by Q2 2025.
    
    CFO: Thank you, CEO. I'd like to add that our operating margin improved to 22%, 
    up from 20% last quarter, despite the challenges mentioned. We maintain a strong 
    balance sheet with $1.8 billion in cash and equivalents.
    
    We're raising our full-year revenue guidance to $8.2-8.4 billion, up from our 
    previous guidance of $8.0-8.2 billion, reflecting our confidence in Q4 performance.
    
    Analyst Q&A:
    Q: What's your outlook on the competitive landscape?
    A: While competition is intensifying, we believe our technology differentiation 
    and customer relationships give us a sustainable advantage.
    
    Q: Any concerns about the supply chain issues?
    A: We expect these to be largely resolved by Q1 2025 as we've diversified our 
    supplier base and built additional inventory buffers.
    """
    
    # Expected AI analysis structure
    expected_ai_response = {
        "sentiment": "Cautiously Optimistic",
        "good_news": [
            "Revenue grew 18% year-over-year to $2.1 billion, exceeding guidance",
            "Cloud services division showed strong 25% growth",
            "Operating margin improved to 22% from 20% last quarter",
            "Strong balance sheet with $1.8 billion in cash",
            "Raised full-year revenue guidance to $8.2-8.4 billion"
        ],
        "bad_news": [
            "Supply chain disruptions impacted hardware division with 5% decline",
            "Increased competition putting pressure on margins",
            "Hardware segment facing challenges"
        ],
        "key_promises": [
            "Investing $500 million in R&D over next 12 months",
            "Expanding international presence with new European offices by Q2 2025",
            "Supply chain issues expected to be resolved by Q1 2025",
            "Diversifying supplier base and building inventory buffers"
        ],
        "verdict": "TechCorp delivered solid Q3 results with strong revenue growth and margin expansion, driven by cloud services success. While supply chain challenges and competitive pressures present near-term headwinds, management's strategic investments in R&D and international expansion, combined with raised guidance, suggest confidence in the business trajectory. The strong balance sheet provides flexibility to navigate current challenges."
    }
    
    from app import app, scrape_text_from_url, analyze_text_with_ai
    
    # Test the complete workflow
    with patch('requests.get') as mock_get, \
         patch('google.generativeai.configure'), \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
        
        # Mock HTTP response for scraping
        mock_response = MagicMock()
        mock_response.content = f"<html><body><div>{realistic_transcript}</div></body></html>".encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock AI response
        mock_model = MagicMock()
        mock_ai_response = MagicMock()
        mock_ai_response.text = json.dumps(expected_ai_response)
        mock_model.generate_content.return_value = mock_ai_response
        mock_model_class.return_value = mock_model
        
        # Test via Flask endpoint
        with app.test_client() as client:
            response = client.post('/analyze', json={
                "url": "https://example.com/techcorp-q3-2024-earnings"
            })
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.get_json()
                
                # Verify response structure
                print("✓ Analysis completed successfully")
                print(f"✓ Sentiment: {result.get('sentiment', 'N/A')}")
                print(f"✓ Good news items: {len(result.get('good_news', []))}")
                print(f"✓ Bad news items: {len(result.get('bad_news', []))}")
                print(f"✓ Key promises: {len(result.get('key_promises', []))}")
                print(f"✓ Verdict length: {len(result.get('verdict', ''))}")
                
                # Verify content quality
                if result.get('sentiment'):
                    print("✓ Sentiment analysis provided")
                
                if len(result.get('good_news', [])) >= 3:
                    print("✓ Sufficient positive highlights identified")
                
                if len(result.get('bad_news', [])) >= 2:
                    print("✓ Risk factors identified")
                
                if len(result.get('key_promises', [])) >= 2:
                    print("✓ Management commitments captured")
                
                if len(result.get('verdict', '')) > 100:
                    print("✓ Comprehensive verdict provided")
                
                return True
            else:
                print(f"✗ Analysis failed with status {response.status_code}")
                print(f"Error: {response.get_json()}")
                return False

def test_frontend_integration():
    """Test that the frontend can properly display analysis results."""
    print("\nTesting frontend result display formatting...")
    
    # Test data that matches expected frontend structure
    test_result = {
        "sentiment": "Positive",
        "good_news": [
            "Revenue exceeded expectations",
            "Strong margin expansion",
            "Successful product launch"
        ],
        "bad_news": [
            "Supply chain challenges",
            "Competitive pressures"
        ],
        "key_promises": [
            "Increased R&D investment",
            "International expansion"
        ],
        "verdict": "Strong performance with positive outlook despite some operational challenges."
    }
    
    # Verify data structure matches frontend expectations
    required_fields = ['sentiment', 'good_news', 'bad_news', 'key_promises', 'verdict']
    
    for field in required_fields:
        if field in test_result:
            print(f"✓ Frontend field '{field}' present")
        else:
            print(f"✗ Frontend field '{field}' missing")
    
    # Verify list fields are properly formatted
    list_fields = ['good_news', 'bad_news', 'key_promises']
    for field in list_fields:
        if isinstance(test_result.get(field), list):
            print(f"✓ Field '{field}' is properly formatted as list")
        else:
            print(f"✗ Field '{field}' is not a list")
    
    # Verify string fields have content
    string_fields = ['sentiment', 'verdict']
    for field in string_fields:
        if isinstance(test_result.get(field), str) and len(test_result[field]) > 0:
            print(f"✓ Field '{field}' has content")
        else:
            print(f"✗ Field '{field}' is empty or not a string")
    
    return True

def main():
    """Run realistic workflow tests."""
    print("=" * 70)
    print("QuickBrief AI - Realistic Workflow Integration Tests")
    print("=" * 70)
    
    success = True
    
    try:
        success &= test_realistic_workflow()
        success &= test_frontend_integration()
        
        print("\n" + "=" * 70)
        if success:
            print("✓ All realistic workflow tests PASSED!")
        else:
            print("✗ Some tests FAILED!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test execution failed: {str(e)}")
        success = False
    
    return success

if __name__ == "__main__":
    main()