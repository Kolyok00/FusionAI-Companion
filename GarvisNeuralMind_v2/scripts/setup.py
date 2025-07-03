#!/usr/bin/env python3
"""
GarvisNeuralMind Setup Script
Helps set up the project environment and dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} sikeres")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} sikertelen: {e}")
        print(f"Error output: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ szükséges! Jelenlegi verzió:", sys.version)
        return False
    print(f"✅ Python verzió OK: {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories():
    """Create necessary directories"""
    dirs = ["logs", "data", "temp"]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {dir_name}")


def setup_environment():
    """Set up environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("📝 Created .env file from template")
        print("⚠️  Please edit .env file and add your API keys!")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example found")


def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        return run_command("pip install -r requirements.txt", "Dependencies telepítése")
    else:
        print("❌ requirements.txt not found")
        return None


def check_docker():
    """Check if Docker is available"""
    docker_check = run_command("docker --version", "Docker ellenőrzése")
    if docker_check:
        docker_compose_check = run_command("docker-compose --version", "Docker Compose ellenőrzése")
        return bool(docker_compose_check)
    return False


def main():
    """Main setup function"""
    print("🚀 GarvisNeuralMind Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if install_dependencies():
        print("✅ Python dependencies telepítve")
    else:
        print("❌ Dependency telepítés sikertelen")
        return 1
    
    # Check Docker
    if check_docker():
        print("✅ Docker és Docker Compose elérhető")
        print("💡 Docker-rel való futtatáshoz használd: docker-compose up -d")
    else:
        print("⚠️  Docker nem elérhető - csak Python módban futtatható")
    
    print("\n🎯 Setup befejezve!")
    print("\nKövetkező lépések:")
    print("1. Edit .env file és add meg az API kulcsaidat")
    print("2. Futtasd: python src/main.py")
    print("3. Nyisd meg a böngészőben: http://localhost:8000/docs")
    
    return 0


if __name__ == "__main__":
    exit(main())