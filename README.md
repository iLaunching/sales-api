# Sales API

AI-powered personalized sales conversations and lead qualification system.

## Overview

The Sales API provides intelligent sales conversations that:
- **Discover** user needs through conversational questioning
- **Personalize** pitches based on industry, pain points, and goals
- **Qualify** leads with scoring (0-100) and tier classification
- **Learn** from successful conversions to improve over time
- **Handoff** high-quality leads to Auth API with enriched profile data

## Architecture

```
Frontend Landing Page
        ↓
Sales API (FastAPI)
    ├── AI Sales Agent (LLM-powered conversations)
    ├── Qualification Service (lead scoring)
    ├── MCP Client (pre-built templates & stories)
    └── Context Retrieval (vector DB)
        ↓
Sales Database (PostgreSQL + Vector DB)
        ↓
Auth API Handoff (with sales_profile_id)
```

## Key Components

### 1. AI Sales Agent (`services/ai_sales_agent.py`)
- Conversational flow management
- LLM integration (OpenAI/Anthropic)
- Stage-based prompting (greeting → discovery → qualification → pitch → handoff)
- Insight extraction from user responses

### 2. Qualification Service (`services/qualification_service.py`)
- Lead scoring algorithm (0-100)
- Quality tiers: high (70+), medium (40-70), low (<40)
- Engagement metrics
- Handoff decision logic

### 3. MCP Client (`services/mcp_client.py`)
- Retrieves pitch templates
- Finds relevant success stories
- Matches features to needs
- Handles objections
- Calculates value/ROI

### 4. Database Models (`models/sales_conversation.py`)
- Conversation history
- User profile data
- Qualification scores
- Engagement metrics
- A/B test variants

## API Endpoints

### Create Conversation
```http
POST /api/sales/conversations
{
  "session_id": "string",
  "email": "user@example.com"  # optional
}
```

### Send Message
```http
POST /api/sales/message
{
  "session_id": "string",
  "message": "string",
  "email": "user@example.com"  # optional
}

Response:
{
  "message": "AI response",
  "stage": "discovery",
  "qualification_score": 45.5,
  "should_handoff": false,
  "sales_profile_id": null
}
```

### WebSocket (Real-time)
```
ws://localhost:8080/api/sales/ws/{session_id}
```

### Get Conversation
```http
GET /api/sales/conversations/{conversation_id}
GET /api/sales/conversations/session/{session_id}
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Configure required services:
   - PostgreSQL database
   - Redis for sessions
   - Qdrant for vector storage
   - OpenAI/Anthropic API keys
   - Auth API connection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the server
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Conversation Stages

1. **Greeting** - Initial welcome, ask what brought them here
2. **Discovery** - Learn about business, pain points, goals
3. **Qualification** - Assess budget signals, urgency, authority
4. **Pitch** - Personalized value proposition with matched features
5. **Handoff** - Guide to signup with enriched profile data

## Qualification Scoring

### Score Components (0-100)
- Pain points discovered: 25 points max
- Goals identified: 20 points max
- Budget signals: 20 points max
- Urgency level: 15 points max
- Decision authority: 15 points max
- Company info completeness: 5 points max

### Quality Tiers
- **High** (70+): Decision-maker, clear pain points, high urgency
- **Medium** (40-70): Good fit, some discovery needed
- **Low** (<40): Early stage, needs more qualification

## Integration with Auth API

When a lead is qualified (score ≥ 60) and ready to sign up:

1. Sales API creates `sales_profile_id`
2. Packages discovery data:
   - Industry, company, role
   - Pain points and goals
   - Qualification score
   - Conversation insights
3. Sends to Auth API's signup endpoint
4. Auth API creates user with enriched context
5. Frontend receives `sales_profile_id` for tracking

## Development Roadmap

### Phase 0: Foundation ✅
- [x] Basic FastAPI structure
- [x] Database models
- [x] API routes
- [x] AI Sales Agent skeleton
- [x] Qualification service

### Phase 1: Personalization
- [ ] Vector DB integration for retrieval
- [ ] MCP server implementation
- [ ] LLM pitch generation
- [ ] Feature matching

### Phase 2: Optimization
- [ ] Qualification algorithm tuning
- [ ] Response caching
- [ ] A/B testing framework
- [ ] Performance optimization

### Phase 3: Learning
- [ ] Conversion tracking
- [ ] Pattern analysis
- [ ] Question flow optimization
- [ ] Analytics dashboard

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Test specific module
pytest tests/test_sales_agent.py
```

## Deployment (Railway)

```bash
# Deploy to Railway
railway up

# Set environment variables in Railway dashboard
# - DATABASE_URL
# - REDIS_URL
# - OPENAI_API_KEY
# - etc.

# Monitor logs
railway logs
```

## Monitoring

- **Sentry**: Error tracking (configure SENTRY_DSN)
- **Structured Logging**: JSON logs for analysis
- **Analytics**: Conversion rates, qualification scores, engagement metrics

## License

Proprietary - Internal use only
