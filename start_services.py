#!/usr/bin/env python3
"""
Start script for Dude Manga services
Starts both the Flask proxy and Playwright services
"""

import subprocess
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

def start_service(script_path, service_name, port):
    """Start a service in a subprocess"""
    print(f"Starting {service_name} on port {port}...")
    try:
        process = subprocess.Popen([
            sys.executable, script_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ {service_name} started successfully (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return None

def main():
    print("🚀 Starting Dude Manga Services...")
    print("=" * 50)
    
    # Start Playwright service first
    playwright_process = start_service(
        "playwright_service/app.py",
        "Playwright Service",
        os.getenv('PLAYWRIGHT_PORT', 5000)
    )
    
    if not playwright_process:
        print("❌ Failed to start Playwright service. Exiting.")
        sys.exit(1)
    
    # Wait a moment for Playwright to initialize
    time.sleep(3)
    
    # Start Flask proxy
    flask_process = start_service(
        "proxy/app.py",
        "Flask Proxy",
        os.getenv('FLASK_PORT', 3006)
    )
    
    if not flask_process:
        print("❌ Failed to start Flask proxy. Exiting.")
        playwright_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All services started successfully!")
    print(f"📱 React Frontend: http://localhost:{os.getenv('REACT_PORT', 3005)}")
    print(f"🔗 Flask Proxy: http://localhost:{os.getenv('FLASK_PORT', 3006)}")
    print(f"🕷️  Playwright Service: http://localhost:{os.getenv('PLAYWRIGHT_PORT', 5000)}")
    print("\nPress Ctrl+C to stop all services...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        flask_process.terminate()
        playwright_process.terminate()
        print("✅ All services stopped.")

if __name__ == "__main__":
    main() 