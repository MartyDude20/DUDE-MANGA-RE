#!/usr/bin/env python3
"""
Setup script for Dude Manga
Installs dependencies and sets up the project
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    print("❌ Node.js is not installed or not in PATH")
    return False

def setup_environment():
    """Set up environment file"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from env.example")
            print("⚠️  Please edit .env and add your Firecrawl API key")
        else:
            print("⚠️  No env.example found, please create .env manually")
    else:
        print("✅ .env file already exists")

def main():
    print("🚀 Setting up Dude Manga...")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        print("Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browsers"):
        sys.exit(1)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Firecrawl API key")
    print("2. Run 'python start_services.py' to start all services")
    print("3. Or run 'start_services.bat' on Windows")
    print("4. Open http://localhost:3005 in your browser")
    print("\nHappy manga hunting! 🎭")

if __name__ == "__main__":
    main() 