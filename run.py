#!/usr/bin/env python3
"""
Simple run script for Jusbook Chatbot
Alternative to running app.py directly
"""

import uvicorn
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the Jusbook chatbot application"""
    print("🤖 Starting Jusbook AI Chatbot...")
    print("📱 Building intelligent booking assistant...")
    port = int(os.getenv("PORT", "8000"))
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"📋 API documentation at: http://localhost:{port}/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=os.getenv("RELOAD", "true").lower() == "true",  # Enable auto-reload for development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Jusbook Chatbot. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
