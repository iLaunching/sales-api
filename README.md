# Sales API - PostgreSQL + Redis + AI

FastAPI server with PostgreSQL, Redis caching, and AI-powered sales conversations.

## What This Has

✅ FastAPI server
✅ PostgreSQL database
✅ Redis caching
✅ AI responses via LLM Gateway
✅ Conversation storage
✅ Message history
✅ Session caching (30min TTL)
✅ Sales-focused AI agent

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
LLM_GATEWAY_URL=https://ilaunching-llm-server-production.up.railway.app
```

## Endpoints

- `GET /health` - Health check
- `GET /` - Service info
- `POST /api/sales/conversations` - Create conversation
- `GET /api/sales/conversations/{session_id}` - Get conversation (cached)
- `POST /api/sales/message` - Send message with AI response

## Next Steps

- ✅ PostgreSQL (DONE)
- ✅ Redis (DONE)
- ✅ AI responses (DONE)
- ⏳ MCP tools integration
- ⏳ Qdrant vector search
