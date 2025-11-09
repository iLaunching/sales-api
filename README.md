# Sales API - Full Stack: PostgreSQL + Redis + AI + MCP

Complete FastAPI server with database, caching, AI, and MCP tools for sales.

## What This Has

✅ FastAPI server
✅ PostgreSQL database
✅ Redis caching
✅ AI responses via LLM Gateway
✅ MCP Sales Tools (objections, pitches, ROI)
✅ Conversation storage
✅ Message history
✅ Session caching (30min TTL)
✅ Sales-focused AI agent

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
LLM_GATEWAY_URL=https://your-llm-gateway.railway.app
MCP_SERVER_URL=https://your-mcp-server.railway.app

# Optional LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
```

## Endpoints

**Core:**
- `GET /health` - Health check
- `GET /` - Service info

**Conversations:**
- `POST /api/sales/conversations` - Create conversation
- `GET /api/sales/conversations/{session_id}` - Get conversation (cached)
- `POST /api/sales/message` - Send message with AI response

**MCP Tools:**
- `POST /api/mcp/objection` - Handle sales objection
- `POST /api/mcp/pitch` - Get industry pitch template
- `POST /api/mcp/value` - Calculate ROI/value proposition

## Next Steps

- ✅ PostgreSQL (DONE)
- ✅ Redis (DONE)
- ✅ AI responses (DONE)
- ✅ MCP tools (DONE)
- ⏳ Qdrant vector search (Optional)
