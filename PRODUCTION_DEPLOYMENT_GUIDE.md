# Production Deployment Guide

**Last Updated:** November 14, 2025  
**Service:** Streaming Content API (sales-api-minimal)  
**Platform:** Railway  
**Status:** Production Ready ✅

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Railway Deployment](#railway-deployment)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)

---

## Prerequisites

### Required Tools
- Git installed and configured
- GitHub account with repository access
- Railway account (https://railway.app)
- Python 3.11+ (for local testing)

### Repository Structure
```
sales-api-minimal/
├── main.py                          # FastAPI application
├── content_processor.py             # Content processing logic
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container configuration
├── railway.json                     # Railway configuration
├── PRODUCTION_API_REFERENCE.md      # API documentation
└── PRODUCTION_DEPLOYMENT_GUIDE.md   # This file
```

---

## Railway Deployment

### Option 1: Automatic Deployment (Recommended)

Railway is configured for automatic deployment from GitHub.

**Steps:**

1. **Push to GitHub**
   ```bash
   cd /workspaces/Ilaunching-SERVERS
   git add sales-api-minimal/
   git commit -m "Deploy production-hardened streaming API"
   git push origin main
   ```

2. **Railway Auto-Deploys**
   - Detects changes on main branch
   - Builds Docker container
   - Deploys automatically
   - Assigns public URL

3. **Get Deployment URL**
   - Go to Railway dashboard
   - Click on `sales-api-minimal` service
   - Find public URL (e.g., `sales-api-production-3088.up.railway.app`)

**Deployment Time:** 2-3 minutes

### Option 2: Manual Deployment

If automatic deployment fails:

1. **Login to Railway**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Link Project**
   ```bash
   cd sales-api-minimal
   railway link
   ```

3. **Deploy**
   ```bash
   railway up
   ```

---

## Configuration

### Production Settings

Current production configuration in `main.py`:

```python
# Rate Limiting
MAX_REQUESTS_PER_SESSION = 100      # Requests per session
MAX_SESSION_DURATION = 3600         # 1 hour (seconds)
MAX_CONTENT_SIZE = 100_000          # 100KB (bytes)

# Timeouts
IDLE_TIMEOUT = 300                  # 5 minutes (seconds)
CHUNK_TIMEOUT = 5.0                 # 5 seconds per chunk

# Content Processing (content_processor.py)
MAX_CONTENT_SIZE = 1_000_000        # 1MB total limit
max_chunk_size = 1000               # 1KB per chunk
```

### Adjusting Limits

**For Higher Traffic:**

```python
MAX_REQUESTS_PER_SESSION = 1000     # 10x more requests
MAX_SESSION_DURATION = 7200         # 2 hours
MAX_CONTENT_SIZE = 1_000_000        # 1MB (matches processor)
```

**After Changes:**
1. Commit changes to GitHub
2. Railway auto-deploys in 2-3 minutes
3. Verify new limits in `connected` message

### Environment Variables

Railway automatically sets:
- `PORT`: Service port (usually 8080)
- `RAILWAY_ENVIRONMENT`: "production"

Optional variables (set in Railway dashboard):
- `LOG_LEVEL`: "DEBUG", "INFO", "WARNING", "ERROR" (default: INFO)
- `MAX_WORKERS`: Number of Uvicorn workers (default: 1)

**To Set:**
1. Go to Railway dashboard
2. Click service → Variables tab
3. Add variable
4. Redeploy if needed

---

## Verification

### 1. Check Deployment Status

**Railway Dashboard:**
- Go to https://railway.app/dashboard
- Click on `sales-api-minimal` service
- Check "Deployments" tab
- Look for green "Success" status

**Via API:**
```bash
curl https://sales-api-production-3088.up.railway.app/
```

Expected response:
```json
{
  "service": "Sales API",
  "status": "operational",
  "version": "2.4.1"
}
```

### 2. Test WebSocket Connection

**Using websocat (CLI tool):**
```bash
# Install websocat
brew install websocat  # macOS
# or download from https://github.com/vi/websocat

# Test connection
websocat wss://sales-api-production-3088.up.railway.app/ws/stream/test-session
```

Expected: `{"type":"connected","session_id":"test-session",...}`

**Using JavaScript:**
```javascript
const ws = new WebSocket('wss://sales-api-production-3088.up.railway.app/ws/stream/test-123');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onopen = () => ws.send(JSON.stringify({
  type: 'stream_request',
  content: 'Hello world!',
  content_type: 'text',
  speed: 'normal'
}));
```

### 3. Verify Production Features

**Test Rate Limiting:**
```bash
# Should succeed 100 times, then fail
for i in {1..105}; do
  echo "Request $i"
  # Send request via WebSocket
done
```

Expected: Error after 100 requests

**Test Content Size Limit:**
```bash
# Create 150KB content (exceeds 100KB limit)
large_content=$(python3 -c "print('x' * 150000)")
# Send via WebSocket
```

Expected: `CONTENT_TOO_LARGE` error

**Test Session Timeout:**
- Connect to WebSocket
- Wait 5 minutes without activity
- Expected: `IDLE_TIMEOUT` error and disconnect

### 4. Performance Check

**Latency Test:**
```bash
time curl https://sales-api-production-3088.up.railway.app/
```

Expected: < 200ms

**Streaming Performance:**
- Use test interface: http://localhost:5174/websocket-test
- Click "Plain Text" → should stream in ~1 second
- Click "MEGA Complex HTML" → should complete in 2-3 seconds
- Check browser console for timing logs

---

## Monitoring

### Railway Built-in Monitoring

**Metrics Available:**
1. **Deployments Tab**
   - Build time
   - Deploy status
   - Deployment logs

2. **Metrics Tab**
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

3. **Logs Tab**
   - Real-time logs
   - Filter by level
   - Search functionality

**Accessing Logs:**
```bash
railway logs
# or via dashboard
```

### Application Logging

**Log Levels Used:**

| Level | Use Case | Example |
|-------|----------|---------|
| INFO | Normal operations | "✅ Stream complete: 45 chunks" |
| WARNING | Non-critical issues | "⚠️ Rate limit approaching" |
| ERROR | Errors with recovery | "❌ Chunking failed, using fallback" |
| DEBUG | Development only | Chunk contents |

**Key Log Messages:**

```
✅ WebSocket connected: user-session-123
📊 Content analysis: {"complexity": "medium", ...}
⚡ Adaptive speed selected: normal
🔄 Stream request #5: session=..., length=1500
✅ Stream complete: 45 chunks sent
🔌 WebSocket disconnected: user-session-123 (requests: 5)
```

**Error Patterns to Monitor:**

```
❌ Rate limit exceeded        → User hitting limits
❌ Content too large          → Users sending large content
❌ Session timeout            → Long-running sessions
❌ Stream processing error    → Processing failures
```

### Performance Metrics

**In Response Metadata:**
```json
{
  "processing_time_ms": 12.5,
  "avg_chunk_size": 25,
  "chunk_count": 45
}
```

**What to Monitor:**
- `processing_time_ms` > 100ms → Slow processing
- `chunk_count` > 200 → Large content
- Request rate > 50/minute → High traffic

### Alerting (Optional)

**Set up alerts for:**
1. High error rate (> 5% of requests)
2. Slow response time (> 500ms)
3. High memory usage (> 80%)
4. Connection failures

**Tools:**
- Railway alerts (in dashboard)
- External: Sentry, New Relic, Datadog
- Custom: webhook notifications

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

**Symptoms:**
- Railway shows "Failed" status
- Build errors in logs

**Solutions:**

1. **Check Dockerfile**
   ```dockerfile
   # Ensure content_processor.py is copied
   COPY content_processor.py .
   ```

2. **Verify requirements.txt**
   ```txt
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   websockets==12.0
   # ... other dependencies
   ```

3. **Check logs**
   ```bash
   railway logs
   ```

4. **Rebuild**
   ```bash
   git commit --allow-empty -m "Trigger rebuild"
   git push origin main
   ```

#### 2. WebSocket Connection Refused

**Symptoms:**
- Connection fails immediately
- No `connected` message

**Solutions:**

1. **Check URL format**
   ```
   ✅ wss://sales-api-production-3088.up.railway.app/ws/stream/...
   ❌ ws://sales-api-production-3088.up.railway.app/ws/stream/...
   ```

2. **Verify deployment**
   ```bash
   curl https://sales-api-production-3088.up.railway.app/
   ```

3. **Check Railway status**
   - Go to Railway dashboard
   - Verify service is "Active"

#### 3. Rate Limiting Too Aggressive

**Symptoms:**
- Frequent `RATE_LIMIT_EXCEEDED` errors
- Users can't complete workflows

**Solutions:**

1. **Increase limits** (main.py)
   ```python
   MAX_REQUESTS_PER_SESSION = 500  # Increase from 100
   ```

2. **Use unique session IDs**
   ```javascript
   const sessionId = `user-${userId}-${Date.now()}`;
   ```

3. **Split long operations**
   - Use multiple sessions for different tasks

#### 4. Memory Issues

**Symptoms:**
- Railway shows high memory usage
- Service restarts frequently

**Solutions:**

1. **Reduce content size limit**
   ```python
   MAX_CONTENT_SIZE = 50_000  # Reduce from 100KB
   ```

2. **Add memory limits to Dockerfile**
   ```dockerfile
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--limit-concurrency", "50"]
   ```

3. **Upgrade Railway plan** (more RAM)

#### 5. Slow Streaming

**Symptoms:**
- Chunks arrive slowly
- Long pauses between chunks

**Solutions:**

1. **Check network latency**
   ```bash
   ping sales-api-production-3088.up.railway.app
   ```

2. **Optimize chunk size**
   ```python
   # In content_processor.py
   max_chunk_size = 500  # Smaller chunks
   ```

3. **Use faster speed preset**
   ```javascript
   speed: 'fast'  // or 'superfast'
   ```

4. **Check Railway region**
   - Deploy to region closest to users

---

## Scaling

### Vertical Scaling (Railway)

**Current Plan:** Starter ($5/month)
- 512MB RAM
- Shared CPU
- Good for: Testing, small deployments

**Upgrade Path:**
1. **Developer ($20/month)**
   - 8GB RAM
   - More CPU
   - Good for: Production with moderate traffic

2. **Pro ($50/month)**
   - 32GB RAM
   - Priority CPU
   - Good for: High-traffic production

**To Upgrade:**
1. Go to Railway dashboard
2. Account → Billing
3. Choose plan
4. Service auto-restarts with new resources

### Horizontal Scaling

**For Very High Traffic:**

1. **Multiple Railway Services**
   - Deploy same code to multiple services
   - Use load balancer (e.g., Cloudflare)
   - Distribute traffic

2. **Connection Pooling**
   - Implement Redis for session management
   - Share rate limits across instances

3. **Database for Sessions**
   - Add PostgreSQL for persistent sessions
   - Track usage across restarts

**Load Balancer Configuration:**

```nginx
upstream api_servers {
    server sales-api-1.railway.app:443;
    server sales-api-2.railway.app:443;
    server sales-api-3.railway.app:443;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    location /ws/stream/ {
        proxy_pass https://api_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Performance Optimization

**Code-Level:**

1. **Async Processing**
   ```python
   # Already implemented
   async def process_and_stream_content(...)
   ```

2. **Chunk Caching**
   ```python
   # Add Redis caching for repeated content
   from redis import asyncio as aioredis
   
   cache_key = hashlib.md5(content.encode()).hexdigest()
   cached = await redis.get(cache_key)
   if cached:
       chunks = json.loads(cached)
   ```

3. **Connection Reuse**
   ```python
   # Reuse WebSocket connections
   # Implement session pooling
   ```

**Infrastructure:**

1. **CDN for Static Content**
   - Use Cloudflare for caching
   - Edge locations reduce latency

2. **Database Optimization**
   - Add indexes for session lookups
   - Use connection pooling

3. **Monitoring & Profiling**
   - Add APM (Application Performance Monitoring)
   - Identify bottlenecks
   - Optimize slow queries

---

## Rollback Procedure

If deployment causes issues:

### Quick Rollback via Railway

1. **Go to Railway Dashboard**
2. **Deployments Tab**
3. **Find last working deployment**
4. **Click "Redeploy"**

**Time:** ~30 seconds

### Rollback via Git

```bash
# Find last working commit
git log --oneline

# Revert to that commit
git revert <commit-hash>

# Push (triggers auto-deploy)
git push origin main
```

**Time:** ~2-3 minutes

---

## Checklist

### Pre-Deployment

- [ ] All tests passing locally
- [ ] Code reviewed and approved
- [ ] Configuration values set correctly
- [ ] Dependencies updated in requirements.txt
- [ ] Dockerfile includes all necessary files
- [ ] Documentation updated

### Deployment

- [ ] Code pushed to GitHub main branch
- [ ] Railway build successful
- [ ] Deployment shows "Success" status
- [ ] Public URL accessible
- [ ] Health check endpoint returns 200

### Post-Deployment

- [ ] WebSocket connection test passed
- [ ] Basic streaming test completed
- [ ] Rate limiting verified
- [ ] Error handling confirmed
- [ ] Performance metrics acceptable
- [ ] Logs showing expected messages
- [ ] Frontend integration working

### Monitoring (First 24 Hours)

- [ ] Check logs every 2-4 hours
- [ ] Monitor error rate
- [ ] Track response times
- [ ] Watch memory usage
- [ ] Verify rate limiting working
- [ ] Test from different locations

---

## Support & Resources

**Railway Documentation:** https://docs.railway.app  
**FastAPI Documentation:** https://fastapi.tiangolo.com  
**WebSocket Protocol:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

**Project Resources:**
- API Reference: `/sales-api-minimal/PRODUCTION_API_REFERENCE.md`
- Repository: https://github.com/iLaunching/Ilaunching-SERVERS
- Test Interface: http://localhost:5174/websocket-test

---

## Appendix

### Full Deployment Command Reference

```bash
# Check current deployment
railway status

# View logs
railway logs
railway logs --follow

# Open service in browser
railway open

# Run command in Railway environment
railway run python main.py

# Environment variables
railway variables
railway variables set KEY=VALUE

# Link different project
railway link

# Unlink project
railway unlink
```

### Docker Commands (Local Testing)

```bash
# Build image
docker build -t sales-api:latest .

# Run container
docker run -p 8080:8080 sales-api:latest

# Test locally
curl http://localhost:8080/
```

### Testing Scripts

**test_deployment.sh:**
```bash
#!/bin/bash

URL="https://sales-api-production-3088.up.railway.app"

echo "Testing health endpoint..."
curl $URL/

echo "\nTesting WebSocket..."
websocat "wss://sales-api-production-3088.up.railway.app/ws/stream/test-$(date +%s)" &
sleep 2
kill %1

echo "\nDeployment test complete!"
```

---

**Last Updated:** November 14, 2025  
**Status:** Production Ready ✅  
**Deployment Platform:** Railway  
**Current Version:** 2.4.1
