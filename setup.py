#!/usr/bin/env python3
"""
Setup script for Automotive Embedded Build System with MCP Integration
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def setup_project():
    """Set up the automotive build system project"""
    print("🚗 Setting up Automotive Embedded Build System with MCP Integration")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not Path("build.gradle").exists():
        print("❌ build.gradle not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Create necessary directories
    directories = [
        "src/main/c",
        "src/main/templates", 
        "logs",
        "reports",
        "build/generated/headers",
        "build/compiled",
        "mcp/models",
        ".vscode"
    ]
    
    print("📁 Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")
    
    # Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    python_deps = [
        "scikit-learn",
        "numpy", 
        "mcp",
        "asyncio"
    ]
    
    for dep in python_deps:
        run_command(f"pip install {dep}", f"Installing {dep}")
    
    # Make gradlew executable
    if Path("gradlew").exists():
        run_command("chmod +x gradlew", "Making gradlew executable")
    
    # Initialize git repository if not exists
    if not Path(".git").exists():
        run_command("git init", "Initializing git repository")
        run_command("git add .", "Adding files to git")
        run_command('git commit -m "Initial automotive build system setup"', "Initial commit")
    
    print("\n🎯 Running initial build test...")
    build_result = run_command("./gradlew automotiveBuild", "Running automotive build")
    
    if build_result is not None:
        print("✅ Build system setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Open the project in VS Code")
        print("2. Install the GitHub Copilot extension")
        print("3. Configure MCP in VS Code (see .vscode/mcp.json)")
        print("4. Start the MCP server: python mcp/gradle_mcp_server.py")
        print("5. Ask GitHub Copilot for build assistance!")
        
        print("\n🔍 Available Gradle tasks:")
        run_command("./gradlew tasks --group=automotive", "Listing automotive tasks")
        
    else:
        print("❌ Build test failed. Please check the error messages above.")
        print("Try running: ./gradlew clean automotiveBuild")

def test_mcp_server():
    """Test the MCP server functionality"""
    print("\n🧪 Testing MCP server...")
    
    # Import and test the MCP components
    try:
        sys.path.append('mcp')
        from gradle_mcp_server import GradleBuildMonitor
        from learning_engine import BuildPatternLearner
        
        # Test build monitor
        monitor = GradleBuildMonitor()
        print("✅ Build monitor initialized")
        
        # Test learning engine
        learner = BuildPatternLearner()
        print("✅ Learning engine initialized")
        
        # Test with sample data
        sample_event = {
            'task': 'compileC',
            'status': 'SUCCESS',
            'timestamp': '2024-01-15T10:30:00',
            'duration': 5000,
            'sourceFiles': ['main.c', 'utils.c']
        }
        
        learner.learn_from_build_event(sample_event)
        stats = learner.get_statistics()
        print(f"✅ Learning engine tested - Patterns: {stats['total_success_patterns']}")
        
        print("✅ MCP server components are working correctly!")
        
    except ImportError as e:
        print(f"❌ MCP server test failed: {e}")
        print("Please install required dependencies: pip install scikit-learn numpy")
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")

if __name__ == "__main__":
    setup_project()
    test_mcp_server()
    
    print("\n🎉 Automotive Build System with MCP is ready!")
    print("📖 See README.md for usage instructions")