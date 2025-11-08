# Sales API - Minimal Version

Dead simple FastAPI server with ZERO dependencies.

## What This Has

✅ FastAPI server
✅ Health check at `/health`
✅ Root endpoint at `/`
✅ Test endpoint at `/api/sales/message`
✅ Handles Railway's PORT variable

## What This DOESN'T Have

❌ No PostgreSQL
❌ No Redis
❌ No Qdrant
❌ No MCP
❌ No AI/LLM
❌ No database models
❌ No sessions
❌ No authentication

## Test It

```bash
# Local
python main.py

# Test
curl http://localhost:8080/health
curl http://localhost:8080/
curl -X POST http://localhost:8080/api/sales/message \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "session_id": "test-123"}'
```

## Deploy to Railway

1. Push this folder to GitHub repo: `sales-api-minimal`
2. In Railway: New Service → GitHub → `sales-api-minimal`
3. That's it. No environment variables needed.

## Add Features Later

Once this works, we'll add ONE thing at a time:
1. PostgreSQL
2. Redis
3. AI responses
4. MCP tools
5. Qdrant search
