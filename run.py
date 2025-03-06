#!/usr/bin/env python3
"""
Runner script for Balloon Constellation Mission Planner
This script checks dependencies and runs the Flask application.
"""

import os
import sys
import shutil
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import requests
        import pandas
        import numpy
        
        print("✅ Basic dependencies verified.")
        
        # Check for optional dependencies (LLM functionality)
        try:
            import langchain
            import openai
            print("✅ LLM dependencies verified.")
            return True
        except ImportError:
            print("⚠️  LLM dependencies not found. The application will run, but LLM-based analysis features will be disabled.")
            print("   Install with: pip install langchain openai")
            return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install the required dependencies with: pip install -r requirements.txt")
        return False

def check_file_structure():
    """Check if the required file structure exists"""
    required_files = [
        'app.py',
        'balloon_data_fetcher.py',
        'llm_analyzer.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/map.js',
        'static/js/analysis.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        
        print("\nWould you like to run setup.py to create the directory structure? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            # Check if setup.py exists, otherwise create it
            if not Path('setup.py').exists():
                print("setup.py not found. Creating it...")
                # You would need to implement the creation of setup.py here
                return False
            
            # Run setup.py
            print("Running setup.py...")
            try:
                import setup
                setup.main()
                return True
            except Exception as e:
                print(f"❌ Error running setup.py: {e}")
                return False
        else:
            return False
    
    return True

def main():
    """Main entry point"""
    print("\n🎈 Balloon Constellation Mission Planner 🎈")
    print("----------------------------------------")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check file structure
    if not check_file_structure():
        print("❌ Please ensure all required files are in place before running the application.")
        return 1
    
    # Import the app module
    try:
        from app import app
        
        # Get port from environment variable or use default
        port = int(os.environ.get("PORT", 5000))
        
        print(f"\n🚀 Starting the application on port {port}...")
        print(f"   URL: http://localhost:{port}")
        print("   Press Ctrl+C to stop the server.")
        
        # Run the Flask app
        app.run(debug=True, host="0.0.0.0", port=port)
        return 0
    
    except ImportError as e:
        print(f"❌ Error importing application modules: {e}")
        print("Please make sure all project files are in the correct locations.")
        return 1
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())