# Test Mode - Format Demonstration

The LLM now has a **TEST MODE** that lets you request different text formats and node types to see how they animate in the editor.

## How to Enable Test Mode

### Option 1: WebSocket (Streaming)
Add `"test_mode": true` to your stream request:

```json
{
  "type": "stream",
  "content": "show me a code block",
  "test_mode": true,
  "speed": "normal"
}
```

### Option 2: REST API
Add `"test_mode": true` to your message request:

```json
{
  "session_id": "test-session",
  "message": "give me a list",
  "test_mode": true
}
```

## Available Commands in Test Mode

Once test mode is enabled, you can ask the AI to demonstrate different formats:

### Text Formatting
- "Show me bold and italic" → Demonstrates **bold** and *italic* text
- "Send formatted text" → Mix of bold, italic, code, etc.

### Lists
- "Show me a list" → Bullet list
- "Send numbered list" → Ordered list  
- "Give me tasks" → Task list with checkboxes
- "Show nested lists" → Multi-level lists

### Code Blocks
- "Send me code" → Code block with syntax highlighting
- "Show Python code" → Python example
- "JavaScript example" → JavaScript code block
- "Multiple code blocks" → Several code blocks in different languages

### Headings
- "Show headings" → Different heading levels (## H2, ### H3, etc.)
- "Give me a structured response" → Headings + content

### Tables
- "Show me a table" → Markdown table
- "Create a comparison table" → Table with data

### Mixed Content
- "Show all formats" → Comprehensive example with multiple formats
- "Give me rich content" → Mix of lists, code, headings, etc.
- "Demonstrate everything" → Every format type

### Blockquotes
- "Show a quote" → Blockquote example
- "Give me important notes" → Blockquoted content

## Example Frontend Integration

### React/TypeScript
```typescript
// In your streaming hook or API call
const sendTestMessage = async (message: string) => {
  const ws = new WebSocket('wss://your-api.up.railway.app/ws');
  
  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: 'stream',
      content: message,
      test_mode: true,  // Enable test mode
      speed: 'normal'
    }));
  };
};

// Usage
sendTestMessage("show me a code block");
sendTestMessage("give me a task list");
sendTestMessage("demonstrate everything");
```

### Adding a Test Mode Toggle
```tsx
// In your chat interface
const [testMode, setTestMode] = useState(false);

<div className="test-mode-toggle">
  <label>
    <input 
      type="checkbox" 
      checked={testMode}
      onChange={(e) => setTestMode(e.target.checked)}
    />
    Test Mode (Format Demonstration)
  </label>
</div>

// In your send function
const handleSend = (message: string) => {
  addToQueue({
    id: generateId(),
    config: {
      turnId: turnId,
      content: message,
      test_mode: testMode,  // Pass the flag
    }
  });
};
```

## What Happens in Test Mode

1. **Different System Prompt**: The AI switches from sales mode to test mode
2. **Format-Focused Responses**: AI demonstrates the requested format clearly
3. **Same Animations Apply**: All animations work the same way
4. **Educational**: Helps you understand what formats are available

## Testing Animation Performance

Test mode is perfect for:
- ✅ Verifying all node types animate correctly
- ✅ Testing animation smoothness with complex content
- ✅ Checking code block streaming
- ✅ Validating table rendering
- ✅ Ensuring task lists are interactive
- ✅ Performance testing with large responses

## Switching Back to Sales Mode

Simply remove or set `test_mode: false` in your requests to return to normal sales conversation mode.

## Example Conversation Flow

```
User: "show me everything"
AI: (Sends comprehensive Markdown with all formats)

User: "now just code"  
AI: (Sends multiple code blocks in different languages)

User: "give me a table"
AI: (Sends formatted table)

User: "tasks please"
AI: (Sends interactive task list)
```

All of these will stream with the smooth wave and fade animations you've configured!
