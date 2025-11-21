# System Message Troubleshooting Guide

## Overview
System messages are pre-written markdown messages that are streamed through the API like LLM responses but without requiring an actual LLM call. This is more efficient and ensures consistent welcome messages.

## How System Messages Work

### 1. **Message Format**
System messages use a special format with optional user personalization:
```
__SYSTEM_MESSAGE_TYPE__              # Without user name
__SYSTEM_MESSAGE_TYPE__|USER:Name    # With user name
```

### 2. **Available Message Types**
Defined in `constants/system_messages.py`:
- `__SYSTEM_SALES_WELCOME__` - Welcome message for sales stage
- `__SYSTEM_STAGE_TRANSITION__` - Stage transition messages
- `__SYSTEM_FEATURE_INTRO__` - Feature introduction messages
- `__SYSTEM_PROGRESS_UPDATE__` - Progress update messages

### 3. **Detection Flow**
When a message comes in through the WebSocket:

```
User/Frontend sends message
    ↓
WebSocket receives in main.py
    ↓
get_sales_response() in llm_client.py
    ↓
Trim whitespace and parse format
    ↓
Check if base_message matches SYSTEM_MESSAGE_TYPES
    ↓
YES → Return system message (NO LLM CALL)
    ↓
NO → Continue to LLM processing
```

## Common Issues & Solutions

### Issue 1: "I apologize, but I'm having trouble processing your request"

**Symptoms:**
- System message is sent but error message appears instead
- Sometimes works, sometimes doesn't

**Possible Causes:**
1. **Message format mismatch** - Extra whitespace or typo
2. **LLM Gateway timeout** - System message detection failed, fell through to LLM call which timed out
3. **Markdown conversion error** - Valid response but conversion to Tiptap failed

**Debugging Steps:**

1. **Check backend logs for detection:**
   ```bash
   # Look for these log lines:
   📨 Incoming message: '__SYSTEM_SALES_WELCOME__|USER:John'
   🔍 System message types available: ['__SYSTEM_SALES_WELCOME__', ...]
   🔎 Parsed - base_message: '__SYSTEM_SALES_WELCOME__', user_name: 'John'
   ✅ System message MATCHED: __SYSTEM_SALES_WELCOME__, user: John
   📤 Returning system message: 356 chars
   ```

2. **If you see "NOT a system message":**
   - The format doesn't match
   - Check for typos in SYSTEM_MESSAGE_TYPES constants
   - Check frontend is sending correct format

3. **If you see "Processing user message with LLM":**
   - System message was NOT detected
   - It tried to call the LLM Gateway
   - LLM call failed → error message

### Issue 2: System Messages Not Personalized

**Symptoms:**
- Message shows generic "Welcome!" instead of "Welcome, John!"

**Solution:**
1. Check frontend is sending `|USER:Name` format:
   ```typescript
   const messagePayload = userName 
     ? `${messageType}|USER:${userName}` 
     : messageType;
   ```

2. Check backend logs show user name:
   ```
   🔎 Parsed - base_message: '__SYSTEM_SALES_WELCOME__', user_name: 'John'
   ```

3. Verify `get_random_welcome_message()` receives user_name parameter

### Issue 3: Multiple Welcome Messages

**Symptoms:**
- Welcome message appears twice or more

**Solution:**
- Check `hasShownWelcomeRef` is properly set in frontend
- Ensure WebSocket connection check is working
- Verify useEffect dependencies are correct

## Testing System Messages

### Manual Testing Script
Run the test script to verify system message detection:

```bash
cd /workspaces/Ilaunching-SERVERS/sales-api
python test_system_message_flow.py
```

**Expected Output:**
```
✅ Response received: 439 chars
✅ PASSED: User name 'John' found in response
```

### Test Individual Components

**Test 1: System Message Detection**
```python
from constants.system_messages import SYSTEM_MESSAGE_TYPES, get_system_message_response

# Test detection
message_type = SYSTEM_MESSAGE_TYPES['SALES_WELCOME']
response = get_system_message_response(message_type, 'John')
print(response['message'])  # Should contain "John"
```

**Test 2: Frontend Message Format**
```typescript
// In browser console
console.log(SYSTEM_MESSAGE_TYPES.SALES_WELCOME);
// Should output: "__SYSTEM_SALES_WELCOME__"

// Check what's being sent
streaming.addToQueue(`${SYSTEM_MESSAGE_TYPES.SALES_WELCOME}|USER:TestName`, {
  content_type: 'markdown',
  speed: 'normal'
});
```

## Logging Checklist

When debugging system messages, look for these log sequences:

### ✅ Successful System Message Flow
```
📨 Incoming message: '__SYSTEM_SALES_WELCOME__|USER:John'
🔍 System message types available: [...]
🔎 Parsed - base_message: '__SYSTEM_SALES_WELCOME__', user_name: 'John'
✅ System message MATCHED: __SYSTEM_SALES_WELCOME__, user: John
📤 Returning system message: 356 chars
✅ LLM response received: 356 chars
🔄 Converting markdown to Tiptap JSON...
✅ Converted to 12 Tiptap nodes
```

### ❌ Failed Detection (Falls Through to LLM)
```
📨 Incoming message: '__SYSTEM_SALES_WELCOM__'  # Typo!
🔍 System message types available: [...]
🔎 Parsed - base_message: '__SYSTEM_SALES_WELCOM__', user_name: ''
⚠️ NOT a system message. Base message '__SYSTEM_SALES_WELCOM__' not in system types.
💬 Processing user message with LLM: __SYSTEM_SALES_WELCOM__...
❌ LLM call failed: ConnectionError
```

### ❌ Markdown Conversion Error
```
✅ System message MATCHED: __SYSTEM_SALES_WELCOME__, user: John
📤 Returning system message: 356 chars
✅ LLM response received: 356 chars
🔄 Converting markdown to Tiptap JSON...
❌ Markdown conversion failed: [error]
⚠️ Using fallback paragraph node
```

## Robustness Features

The system now includes multiple layers of error handling:

1. **Whitespace Trimming** - Removes leading/trailing spaces from messages
2. **Content Validation** - Verifies response is valid string before returning
3. **Exception Handling** - Catches errors in system message generation
4. **Fallback Messages** - Returns safe default if system message fails
5. **Markdown Fallback** - Uses simple paragraph if Tiptap conversion fails
6. **Detailed Logging** - Every step is logged for debugging

## Configuration

### Frontend Constants
`ilaunching-frontend/src/constants/systemMessages.ts`
```typescript
export const SYSTEM_MESSAGE_TYPES = {
  SALES_WELCOME: '__SYSTEM_SALES_WELCOME__',
  // ... more types
} as const;
```

### Backend Constants
`sales-api/constants/system_messages.py`
```python
SYSTEM_MESSAGE_TYPES = {
    'SALES_WELCOME': '__SYSTEM_SALES_WELCOME__',
    # ... more types
}
```

**CRITICAL:** These must match EXACTLY between frontend and backend!

## Performance Considerations

System messages are designed to be:
- **Fast** - No LLM API call required (~50ms vs ~2-5s)
- **Reliable** - No external dependency on LLM Gateway
- **Cost-effective** - No API usage costs
- **Consistent** - Same welcome experience every time (with randomization)

## Future Enhancements

Potential improvements to consider:
1. Add more system message types (onboarding, tips, etc.)
2. A/B testing different welcome messages
3. Context-aware messages based on user data
4. Multi-language support
5. Time-based greetings (morning/afternoon/evening)

## Support

If system messages are still not working after following this guide:

1. Run the test script and share output
2. Check Railway logs for the backend service
3. Check browser console for frontend errors
4. Verify WebSocket connection is established
5. Confirm environment variables are set correctly
