#!/usr/bin/env python3
"""
System Message Monitor
Watch for system message detection and processing in real-time
"""
import sys
import asyncio
import logging
from datetime import datetime

# Set up logging to show all system message related logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

def monitor_logs():
    """
    Simple monitor that watches for system message patterns
    This should be run alongside the main API server
    """
    print("=" * 70)
    print("System Message Monitor - Watching for system message activity")
    print("=" * 70)
    print()
    print("Looking for these patterns:")
    print("  📨 Incoming message")
    print("  ✅ System message MATCHED")
    print("  ⚠️  NOT a system message")
    print("  ❌ Errors")
    print()
    print("To test, send a system message from the frontend")
    print("Press Ctrl+C to stop")
    print()
    print("-" * 70)
    
    # In a real implementation, this would tail the log file or connect to logging
    # For now, this is a placeholder that developers can enhance
    
    print()
    print("💡 TIP: To monitor logs in real-time, run:")
    print()
    print("   # If running locally:")
    print("   tail -f /path/to/app.log | grep -E '📨|✅|⚠️|❌'")
    print()
    print("   # If on Railway:")
    print("   railway logs --follow | grep -E 'System message|Incoming message'")
    print()
    print("=" * 70)

if __name__ == "__main__":
    try:
        monitor_logs()
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
        sys.exit(0)
