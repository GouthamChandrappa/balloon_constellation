#!/usr/bin/env python3
"""
Setup script for Balloon Constellation Mission Planner
This script creates the necessary directory structure and files.
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the directory structure for the project"""
    # Define the project structure
    structure = {
        'static': {
            'css': ['style.css'],
            'js': ['map.js', 'analysis.js']
        },
        'templates': ['index.html']
    }
    
    # Create the base directory
    base_dir = Path('.')
    
    # Create directories and placeholder files
    for directory, subdirs in structure.items():
        dir_path = base_dir / directory
        
        # Create directory if it doesn't exist
        if not dir_path.exists():
            print(f"Creating directory: {directory}")
            os.makedirs(dir_path, exist_ok=True)
        
        # Handle subdirectories and files
        if isinstance(subdirs, dict):
            for subdir, files in subdirs.items():
                subdir_path = dir_path / subdir
                
                # Create subdirectory if it doesn't exist
                if not subdir_path.exists():
                    print(f"Creating subdirectory: {directory}/{subdir}")
                    os.makedirs(subdir_path, exist_ok=True)
                
                # Create placeholder files
                for file in files:
                    file_path = subdir_path / file
                    if not file_path.exists():
                        print(f"Creating placeholder file: {directory}/{subdir}/{file}")
                        with open(file_path, 'w') as f:
                            f.write(f"/* Placeholder for {file} */\n")
        else:
            # Create placeholder files in the main directory
            for file in subdirs:
                file_path = dir_path / file
                if not file_path.exists():
                    print(f"Creating placeholder file: {directory}/{file}")
                    with open(file_path, 'w') as f:
                        f.write(f"<!-- Placeholder for {file} -->\n")
    
    # Create main application files if they don't exist
    app_files = [
        ('app.py', '# Placeholder for app.py\n'),
        ('balloon_data_fetcher.py', '# Placeholder for balloon_data_fetcher.py\n'),
        ('llm_analyzer.py', '# Placeholder for llm_analyzer.py\n'),
        ('requirements.txt', '# Placeholder for requirements.txt\n'),
        ('README.md', '# Balloon Constellation Mission Planner\n')
    ]
    
    for filename, content in app_files:
        file_path = base_dir / filename
        if not file_path.exists():
            print(f"Creating placeholder file: {filename}")
            with open(file_path, 'w') as f:
                f.write(content)
    
    print("\nDirectory structure created successfully!")

def copy_file_content(source_file, target_file):
    """Copy the content from a source file to a target file"""
    try:
        with open(source_file, 'r') as f:
            content = f.read()
        
        with open(target_file, 'w') as f:
            f.write(content)
        
        print(f"Content copied to {target_file}")
        return True
    except Exception as e:
        print(f"Error copying content to {target_file}: {e}")
        return False

def main():
    """Main entry point"""
    print("\n🎈 Setting up Balloon Constellation Mission Planner 🎈")
    print("---------------------------------------------------")
    
    # Create directory structure
    create_directory_structure()
    
    print("\nSetup complete. You can now add your actual file content.")
    print("Run the application with: python app.py")

if __name__ == "__main__":
    sys.exit(main())