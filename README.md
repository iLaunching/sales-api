# Sales API - Minimal + PostgreSQL

Simple FastAPI server with PostgreSQL for storing conversations.

## What This Has

✅ FastAPI server
✅ PostgreSQL database
✅ Conversation storage
✅ Message history
✅ Health check at `/health`
✅ CRUD endpoints for conversations

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@postgres-sales.railway.internal:5432/railway
```

## Endpoints

- `GET /health` - Health check
- `GET /` - Service info
- `POST /api/sales/conversations` - Create conversation
- `GET /api/sales/conversations/{session_id}` - Get conversation
- `POST /api/sales/message` - Send message (saves to DB)

## Test It

```bash
# Create conversation
curl -X POST https://sales-api-production-3088.up.railway.app/api/sales/conversations \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test-123","email":"test@example.com","name":"John"}'

# Send message
curl -X POST https://sales-api-production-3088.up.railway.app/api/sales/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test-123","message":"I need help with sales"}'

# Get conversation
curl https://sales-api-production-3088.up.railway.app/api/sales/conversations/test-123
```

## Next Steps

- ✅ PostgreSQL (DONE)
- ⏳ Redis for sessions
- ⏳ AI responses with OpenAI
- ⏳ MCP tools integration
- ⏳ Qdrant vector search
