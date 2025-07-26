#!/usr/bin/env python3
"""
Concordance Server Startup Script
Starts the FastAPI server and provides helpful information
"""

import uvicorn
import webbrowser
import time
import os
from pathlib import Path

def main():
    """Start the concordance server"""
    print("🔍 Starting Concordance API Server...")
    print("=" * 50)
    
    # Check if samples directory exists
    samples_dir = Path("samples")
    if not samples_dir.exists():
        print("⚠️  Warning: 'samples' directory not found!")
        print("   Creating samples directory...")
        samples_dir.mkdir()
        print("   Please add .txt corpus files to the 'samples' directory")
    else:
        # List available corpora
        txt_files = list(samples_dir.glob("*.txt"))
        if txt_files:
            print(f"📚 Found {len(txt_files)} corpus files:")
            for txt_file in txt_files[:5]:  # Show first 5
                print(f"   - {txt_file.stem}")
            if len(txt_files) > 5:
                print(f"   ... and {len(txt_files) - 5} more")
        else:
            print("⚠️  No .txt files found in samples directory")
    
    print()
    print("🌐 Server will start at:")
    print("   🎯 Concordancer App: http://localhost:8000/")
    print("   📚 API Documentation: http://localhost:8000/docs")
    print("   🔧 API Status: http://localhost:8000/api")
    print("   📁 Static Files: http://localhost:8000/static/")
    print()
    print("💡 To stop the server, press Ctrl+C")
    print("=" * 50)
    
    try:
        # Start server
        uvicorn.run(
            "concordance_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()