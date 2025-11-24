# QuickBrief AI - System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Frontend (HTML/CSS/JavaScript)               │  │
│  │  • Bootstrap 5 UI Framework                               │  │
│  │  • Responsive Design                                      │  │
│  │  • Real-time Loading Indicators                           │  │
│  │  • Dynamic Result Rendering                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              │ HTTP/HTTPS                         │
│                              ▼                                    │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                              │                                    │
│                    FLASK WEB SERVER                              │
│                    (Python Backend)                              │
│                              │                                    │
│  ┌───────────────────────────┴────────────────────────────┐    │
│  │                    API Endpoints                        │    │
│  │  • GET  /          → Serve main page                    │    │
│  │  • POST /analyze   → Process transcript analysis        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                    │
│  ┌───────────────────────────┴────────────────────────────┐    │
│  │              Request Processing Layer                   │    │
│  │  • Input Validation                                     │    │
│  │  • Error Handling                                       │    │
│  │  • Logging & Monitoring                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                    ┌─────────┴─────────┐                         │
│                    │                   │                          │
│                    ▼                   ▼                          │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │   Web Scraping Service   │  │   AI Analysis Service    │    │
│  │                          │  │                          │    │
│  │  • URL Validation        │  │  • Text Processing       │    │
│  │  • HTTP Requests         │  │  • Prompt Engineering    │    │
│  │  • HTML Parsing          │  │  • JSON Parsing          │    │
│  │  • Text Extraction       │  │  • Response Validation   │    │
│  │  • Content Cleaning      │  │  • Error Recovery        │    │
│  │                          │  │                          │    │
│  │  Libraries:              │  │  Libraries:              │    │
│  │  • Requests              │  │  • Google Generative AI  │    │
│  │  • BeautifulSoup4        │  │  • JSON                  │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
│                    │                   │                          │
└────────────────────┼───────────────────┼──────────────────────────┘
                     │                   │
                     ▼                   ▼
         ┌────────────────────┐  ┌────────────────────────┐
         │  External Website  │  │   Google Gemini API    │
         │                    │  │                        │
         │  • Motley Fool     │  │  • Model: gemini-2.5   │
         │  • Seeking Alpha   │  │  • JSON Response       │
         │  • Company Sites   │  │  • Rate Limiting       │
         │                    │  │  • Error Handling      │
         └────────────────────┘  └────────────────────────┘
```

## Component Details

### 1. Frontend Layer
**Technology:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5

**Responsibilities:**
- User interface rendering
- Form validation and submission
- Asynchronous API communication
- Dynamic result display
- Loading state management
- Error message presentation

**Key Files:**
- `templates/index.html` - Main application template
- `static/style.css` - Fintech-inspired styling
- `static/script.js` - Client-side logic

### 2. Backend Layer
**Technology:** Python 3.8+, Flask, Flask-CORS

**Responsibilities:**
- HTTP request routing
- Request/response handling
- Business logic orchestration
- Error handling and logging
- CORS configuration

**Key Files:**
- `app.py` - Main Flask application

### 3. Web Scraping Service
**Technology:** Requests, BeautifulSoup4

**Responsibilities:**
- URL validation and parsing
- HTTP request execution with timeout
- HTML content parsing
- Script/style tag removal
- Text extraction and cleaning
- Content length validation

**Error Handling:**
- Network timeouts (15 seconds)
- Connection errors
- HTTP error responses (404, 403, 500)
- Invalid URL formats
- Insufficient content

### 4. AI Analysis Service
**Technology:** Google Generative AI SDK

**Responsibilities:**
- API key validation
- Text truncation (20,000 char limit)
- Structured prompt engineering
- AI model interaction
- JSON response parsing
- Field validation

**AI Model:** gemini-2.5-pro
- Latest stable Gemini model
- Optimized for structured output
- JSON response format
- High accuracy analysis

### 5. External Dependencies

**Web Sources:**
- The Motley Fool (fool.com)
- Seeking Alpha (seekingalpha.com)
- Company investor relations pages

**AI Service:**
- Google Gemini API
- Requires API key authentication
- Rate limiting considerations
- Quota management

## Data Flow

### Request Flow:
```
1. User enters URL → Frontend validates
2. Frontend sends POST /analyze → Backend receives
3. Backend validates request → Calls scraping service
4. Scraping service fetches content → Returns text
5. Backend calls AI service → Sends text to Gemini
6. Gemini analyzes text → Returns JSON
7. Backend validates response → Returns to frontend
8. Frontend renders results → User sees analysis
```

### Error Flow:
```
1. Error occurs at any step
2. Service logs error details
3. Service raises exception with user-friendly message
4. Backend catches exception
5. Backend returns appropriate HTTP status code
6. Frontend displays error message to user
7. User can retry with different URL
```

## Security Considerations

### Input Validation:
- URL format validation (client & server)
- Protocol restriction (HTTP/HTTPS only)
- Content type validation
- Request size limits

### API Security:
- Environment variable for API key
- No hardcoded credentials
- Key validation on startup
- Error message sanitization

### Network Security:
- Timeout limits (15 seconds)
- User-agent headers
- CORS configuration
- HTTPS recommended for production

## Performance Optimization

### Response Time Targets:
- Text extraction: < 10 seconds
- AI analysis: < 30 seconds
- Total process: < 60 seconds

### Optimization Strategies:
- Text truncation for large transcripts
- Efficient HTML parsing
- Connection pooling
- Structured prompts for faster AI response

## Scalability Considerations

### Current Architecture:
- Single-threaded Flask development server
- Synchronous request processing
- In-memory processing only

### Production Recommendations:
- Use WSGI server (Gunicorn/uWSGI)
- Implement request queuing
- Add caching layer for repeated URLs
- Load balancing for multiple instances
- Database for analysis history
- Rate limiting per user

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5, CSS3, JavaScript | User interface |
| UI Framework | Bootstrap 5 | Responsive design |
| Backend | Python 3.8+, Flask | Web server |
| Web Scraping | Requests, BeautifulSoup4 | Content extraction |
| AI Integration | Google Generative AI SDK | Text analysis |
| AI Model | Gemini 2.5 Pro | Natural language processing |
| Configuration | python-dotenv | Environment management |
| Testing | unittest, unittest.mock | Quality assurance |

## Deployment Architecture

### Development:
```
Local Machine
├── Python Virtual Environment
├── Flask Development Server (port 5001)
├── Environment Variables (.env file)
└── Local Browser Access
```

### Production (Recommended):
```
Cloud Platform (AWS/GCP/Azure)
├── WSGI Server (Gunicorn)
├── Reverse Proxy (Nginx)
├── SSL/TLS Certificate
├── Environment Variables (Secrets Manager)
├── Logging Service
└── Monitoring & Alerts
```

## Error Handling Strategy

### Three-Layer Error Handling:

1. **Frontend Layer:**
   - Input validation
   - Network error catching
   - User-friendly error display

2. **Backend Layer:**
   - Request validation
   - Service orchestration errors
   - HTTP status code mapping

3. **Service Layer:**
   - Specific error types
   - Detailed logging
   - Exception translation

## Monitoring & Logging

### Logging Levels:
- **INFO**: Successful operations, key milestones
- **ERROR**: Failures, exceptions, invalid states
- **DEBUG**: Detailed execution flow (development only)

### Key Metrics to Monitor:
- Request count per hour
- Average response time
- Error rate by type
- API quota usage
- Successful analysis rate

## Future Enhancements

### Potential Improvements:
1. **Caching**: Store analysis results for repeated URLs
2. **Database**: Persist analysis history
3. **User Accounts**: Save favorite companies
4. **Batch Processing**: Analyze multiple transcripts
5. **Comparison**: Compare multiple quarters
6. **Alerts**: Notify on new transcripts
7. **Export**: PDF/CSV export of results
8. **API**: RESTful API for programmatic access

---

**Architecture Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Production Ready
