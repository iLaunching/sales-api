# Production API Reference - Streaming Content API

**Version:** 2.4.1 Production-Hardened  
**Last Updated:** November 14, 2025  
**Status:** Production Ready ✅

## Overview

Production-ready WebSocket API for streaming content to Tiptap editors with comprehensive safety features, rate limiting, and error handling.

### Key Features
- ✅ Production-grade error handling and recovery
- ✅ Rate limiting and session management
- ✅ XSS protection and content sanitization
- ✅ Adaptive speed and intelligent chunking
- ✅ Backpressure handling for network stability
- ✅ Comprehensive logging and metrics

---

## WebSocket Endpoint

### `/ws/stream/{session_id}`

Production-ready WebSocket endpoint for real-time content streaming.

#### Connection URL
```
wss://sales-api-production-3088.up.railway.app/ws/stream/{session_id}
```

**Parameters:**
- `session_id` (path parameter): Unique identifier for the session (string)

#### Connection Flow

1. **Client Connects** → Server sends `connected` message with limits
2. **Client Sends Request** → Server validates and processes content
3. **Server Streams Chunks** → Client receives chunks in real-time
4. **Stream Completes** → Server sends `stream_complete` message

---

## Message Types

### 1. Server → Client: Connection Confirmation

Sent immediately after WebSocket connection is established.

```json
{
  "type": "connected",
  "session_id": "user-session-123",
  "timestamp": "2025-11-14T10:30:00.000Z",
  "limits": {
    "max_requests": 100,
    "max_content_size": 100000,
    "max_session_duration": 3600
  }
}
```

**Fields:**
- `type`: Always `"connected"`
- `session_id`: Echo of the session ID
- `timestamp`: ISO 8601 timestamp
- `limits`: Current session limits
  - `max_requests`: Maximum requests per session
  - `max_content_size`: Maximum content size in bytes (100KB)
  - `max_session_duration`: Maximum session duration in seconds (1 hour)

---

### 2. Client → Server: Stream Request

Request to stream content with specific parameters.

```json
{
  "type": "stream_request",
  "content": "Your content here...",
  "content_type": "html",
  "speed": "normal",
  "chunk_by": "word"
}
```

**Fields:**
- `type`: Always `"stream_request"`
- `content` (string, required): Content to stream (max 100KB)
- `content_type` (string, required): One of `"text"`, `"html"`, `"markdown"`
- `speed` (string, optional): One of `"slow"`, `"normal"`, `"fast"`, `"superfast"`, `"adaptive"` (default: `"normal"`)
- `chunk_by` (string, optional): One of `"word"`, `"sentence"`, `"paragraph"`, `"character"` (default: `"word"`)

**Content Type Details:**
- `"text"`: Plain text, no processing
- `"html"`: HTML content with sanitization and tag-aware chunking
- `"markdown"`: Converted to HTML, then processed

**Speed Presets:**
- `"slow"`: 300ms delay between chunks (for dramatic effect)
- `"normal"`: 100ms delay (default, readable)
- `"fast"`: 50ms delay (quick but smooth)
- `"superfast"`: 30ms delay (very fast)
- `"adaptive"`: Automatically selected based on content complexity

**Chunking Strategies:**
- `"word"`: Split by words (preserves HTML tags)
- `"sentence"`: Split by sentences
- `"paragraph"`: Split by paragraphs
- `"character"`: Split by characters

---

### 3. Server → Client: Stream Start

Sent before streaming begins, provides metadata.

```json
{
  "type": "stream_start",
  "total_chunks": 45,
  "content_type": "html",
  "metadata": {
    "complexity": "medium",
    "word_count": 150,
    "has_html": true,
    "speed_used": "normal",
    "processing_time_ms": 12.5,
    "avg_chunk_size": 25
  },
  "timestamp": "2025-11-14T10:30:01.000Z"
}
```

**Fields:**
- `type`: Always `"stream_start"`
- `total_chunks`: Number of chunks to be streamed
- `content_type`: Echo of content type
- `metadata`: Processing metadata
  - `complexity`: Content complexity (`"low"`, `"medium"`, `"high"`)
  - `word_count`: Number of words in content
  - `has_html`: Whether HTML tags detected
  - `speed_used`: Speed preset applied
  - `processing_time_ms`: Time taken to process content
  - `avg_chunk_size`: Average chunk size in characters
- `timestamp`: ISO 8601 timestamp

---

### 4. Server → Client: Chunk

Individual content chunk during streaming.

```json
{
  "type": "chunk",
  "data": "<strong>Bold text</strong> and normal text",
  "index": 5,
  "timestamp": "2025-11-14T10:30:01.100Z"
}
```

**Fields:**
- `type`: Always `"chunk"`
- `data`: Content fragment (complete HTML if applicable)
- `index`: Sequential chunk index (0-based)
- `timestamp`: ISO 8601 timestamp

**HTML Guarantees:**
- Chunks contain complete, valid HTML fragments
- Tags are never split across chunks
- Diff-based streaming ensures incremental updates

---

### 5. Server → Client: Stream Complete

Sent after all chunks have been delivered.

```json
{
  "type": "stream_complete",
  "total_chunks": 45,
  "session_id": "user-session-123",
  "timestamp": "2025-11-14T10:30:06.000Z"
}
```

**Fields:**
- `type`: Always `"stream_complete"`
- `total_chunks`: Actual number of chunks sent
- `session_id`: Session identifier
- `timestamp`: ISO 8601 timestamp

---

### 6. Server → Client: Error

Sent when an error occurs.

```json
{
  "type": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Maximum 100 requests per session"
}
```

**Fields:**
- `type`: Always `"error"`
- `code`: Error code (see Error Codes section)
- `message`: Human-readable error description

---

### 7. Client → Server: Ping (Keepalive)

Optional ping to keep connection alive.

```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": "2025-11-14T10:30:01.000Z"
}
```

---

## Error Codes

Comprehensive error codes with HTTP-style naming:

| Code | Description | Resolution |
|------|-------------|------------|
| `RATE_LIMIT_EXCEEDED` | Exceeded 100 requests per session | Wait or start new session |
| `SESSION_TIMEOUT` | Session exceeded 1 hour duration | Reconnect with new session |
| `IDLE_TIMEOUT` | No activity for 5 minutes | Reconnect |
| `CONTENT_TOO_LARGE` | Content exceeds 100KB limit | Split content or reduce size |
| `INVALID_CONTENT_TYPE` | content_type not text/html/markdown | Use valid content type |
| `INVALID_CHUNK_STRATEGY` | chunk_by not word/sentence/paragraph/character | Use valid strategy |
| `CHUNKING_ERROR` | Failed to chunk content | Check content format |
| `PROCESSING_ERROR` | Failed to process content | Retry with simpler content |
| `STREAM_ERROR` | Error during streaming | Retry request |
| `EMPTY_CONTENT` | Content resulted in no chunks | Provide non-empty content |
| `UNKNOWN_MESSAGE_TYPE` | Invalid message type | Use valid message types |
| `INTERNAL_ERROR` | Internal server error | Contact support |

---

## Rate Limits & Quotas

### Current Production Limits

| Limit | Value | Configurable |
|-------|-------|--------------|
| Requests per session | 100 | Yes (see Configuration) |
| Session duration | 1 hour (3600s) | Yes |
| Content size | 100KB (100,000 bytes) | Yes |
| Idle timeout | 5 minutes (300s) | Yes |
| Max chunk size | 1KB (1,000 chars) | Yes |
| Max total content | 1MB (1,000,000 chars) | Yes |

### Increasing Limits

Edit `/sales-api-minimal/main.py`:

```python
# In stream_content_websocket() function
MAX_REQUESTS_PER_SESSION = 100      # Increase for production
MAX_SESSION_DURATION = 3600         # Increase for long sessions
MAX_CONTENT_SIZE = 100_000          # Increase for larger content
```

Edit `/sales-api-minimal/content_processor.py`:

```python
# In chunk_html_by_words() function
MAX_CONTENT_SIZE = 1_000_000        # Overall content limit

# In smart_chunk_content() function
max_chunk_size = 1000               # Per-chunk size limit
```

---

## Security Features

### XSS Protection

Automatic detection and removal of dangerous patterns:

- `javascript:` protocol in URLs
- Inline event handlers (`onclick`, `onload`, etc.)
- `<script>` tags
- `<iframe>` tags
- `data:text/html` URIs

**Example:**
```html
<!-- Input -->
<a href="javascript:alert('XSS')">Click me</a>
<div onclick="malicious()">Content</div>

<!-- Output (sanitized) -->
<a>Click me</a>
<div>Content</div>
```

### Content Sanitization

- Removes dangerous HTML tags
- Strips event handlers
- Validates tag structure
- Preserves safe formatting (bold, italic, lists, tables, etc.)

### Input Validation

- Type checking on all parameters
- Size limits enforced
- Format validation
- Empty content rejection

---

## Performance & Monitoring

### Metrics Included in Response

Every stream includes performance metadata:

```json
{
  "processing_time_ms": 12.5,
  "avg_chunk_size": 25,
  "max_chunk_size": 1000,
  "complexity": "medium"
}
```

### Backpressure Handling

- Automatic delay adjustment when network is slow
- Starts at configured speed (50ms-300ms)
- Increases delay up to 1s if backpressure detected
- Prevents overwhelming slow connections

### Logging

Production-grade logging at all critical points:

- Connection establishment/termination
- Request validation and rate limiting
- Content processing stages
- Chunk transmission
- Error conditions
- Performance metrics

**Log Locations:**
- Railway: View in Railway dashboard → Deployments → Logs
- Local: Console output with color-coded levels

---

## Example Usage

### JavaScript/TypeScript Client

```typescript
// Connect to WebSocket
const ws = new WebSocket('wss://sales-api-production-3088.up.railway.app/ws/stream/my-session-123');

// Handle connection
ws.onopen = () => {
  console.log('Connected!');
};

// Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'connected':
      console.log('Session limits:', message.limits);
      // Send stream request
      ws.send(JSON.stringify({
        type: 'stream_request',
        content: '<strong>Hello</strong> world!',
        content_type: 'html',
        speed: 'normal',
        chunk_by: 'word'
      }));
      break;
      
    case 'stream_start':
      console.log('Starting stream:', message.metadata);
      break;
      
    case 'chunk':
      console.log('Chunk', message.index, ':', message.data);
      // Insert into Tiptap editor
      editor.commands.insertContent(message.data);
      break;
      
    case 'stream_complete':
      console.log('Stream complete!');
      break;
      
    case 'error':
      console.error('Error:', message.code, message.message);
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Handle close
ws.onclose = () => {
  console.log('Disconnected');
};
```

### React Hook Example

```typescript
import { useEffect, useState } from 'react';
import { useEditor } from '@tiptap/react';

function useStreaming(sessionId: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const websocket = new WebSocket(
      `wss://sales-api-production-3088.up.railway.app/ws/stream/${sessionId}`
    );
    
    websocket.onopen = () => {
      setIsConnected(true);
    };
    
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      // Handle messages...
    };
    
    websocket.onclose = () => {
      setIsConnected(false);
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, [sessionId]);
  
  const streamContent = (content: string, options = {}) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify({
        type: 'stream_request',
        content,
        content_type: 'html',
        speed: 'normal',
        chunk_by: 'word',
        ...options
      }));
    }
  };
  
  return { streamContent, isConnected };
}
```

---

## Troubleshooting

### Connection Issues

**Problem:** WebSocket won't connect

**Solutions:**
1. Check URL format: `wss://` not `ws://`
2. Verify Railway deployment is running
3. Check CORS settings (should allow all origins)
4. Verify session_id is valid string

### Rate Limiting

**Problem:** Getting `RATE_LIMIT_EXCEEDED` errors

**Solutions:**
1. Reduce request frequency
2. Start new session (new session_id)
3. Increase `MAX_REQUESTS_PER_SESSION` in code (requires redeploy)

### Content Too Large

**Problem:** Getting `CONTENT_TOO_LARGE` errors

**Solutions:**
1. Split content into smaller pieces
2. Increase `MAX_CONTENT_SIZE` in code (requires redeploy)
3. Compress content before sending

### Streaming Stops Mid-Stream

**Problem:** Stream stops before completion

**Solutions:**
1. Check for network issues
2. Verify no idle timeout (5 minutes)
3. Send periodic pings during long streams
4. Check Railway logs for errors

### HTML Not Rendering

**Problem:** HTML shows as plain text

**Solutions:**
1. Verify `content_type: 'html'` in request
2. Check Tiptap has required extensions (Table, Color, etc.)
3. Verify HTML is valid before sending
4. Check browser console for JavaScript errors

---

## Best Practices

### Session Management
- Use unique session IDs per user/tab
- Include user ID or timestamp in session ID
- Clean up old sessions regularly

### Content Optimization
- Pre-process content before streaming
- Remove unnecessary whitespace
- Validate HTML structure
- Split very large content into multiple requests

### Error Handling
- Always implement error handlers
- Retry failed requests with exponential backoff
- Log errors for debugging
- Show user-friendly error messages

### Performance
- Use `adaptive` speed for automatic optimization
- Choose appropriate `chunk_by` strategy:
  - `word`: Best for most content
  - `sentence`: Better for long text
  - `character`: Smooth but slower
- Monitor `processing_time_ms` metric
- Implement keepalive pings for long sessions

### Security
- Sanitize content on both client and server
- Never trust user input
- Use HTTPS/WSS in production
- Implement authentication for production use

---

## Deployment

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for complete deployment instructions.

### Quick Deploy to Railway

1. Push code to GitHub
2. Railway auto-deploys from main branch
3. Verify deployment in Railway dashboard
4. Test WebSocket endpoint

### Environment Variables

No environment variables required for basic operation. Optional:

- `PORT`: Server port (default: 8080, Railway sets automatically)
- `LOG_LEVEL`: Logging level (default: INFO)

---

## Support & Contact

**Repository:** https://github.com/iLaunching/Ilaunching-SERVERS  
**API Location:** `/sales-api-minimal/`  
**Documentation:** `/sales-api-minimal/PRODUCTION_API_REFERENCE.md`

For issues or questions, create a GitHub issue or contact the development team.

---

## Changelog

### v2.4.1 - Production Hardened (Nov 14, 2025)
- ✅ Added comprehensive rate limiting
- ✅ Session timeout and idle detection
- ✅ Content size validation
- ✅ Backpressure handling
- ✅ Structured error codes
- ✅ Performance monitoring
- ✅ Enhanced logging

### v2.4.0 - WebSocket Integration (Nov 13, 2025)
- ✅ WebSocket endpoint created
- ✅ Diff-based HTML streaming
- ✅ Tag-aware chunking

### v2.2.0 - Content Processing (Nov 12, 2025)
- ✅ HTML sanitization with XSS protection
- ✅ Markdown conversion
- ✅ Adaptive speed selection

---

**Status:** Production Ready ✅  
**Last Tested:** November 14, 2025  
**Test Coverage:** All features validated
