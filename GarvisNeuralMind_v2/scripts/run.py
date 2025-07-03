#!/usr/bin/env python3
"""
GarvisNeuralMind Runner Script
Convenient script to start the application with various options
"""

import argparse
import asyncio
import os
import sys
import subprocess
from pathlib import Path


def check_environment():
    """Check if environment is properly set up"""
    issues = []
    
    # Check if .env file exists
    if not Path(".env").exists():
        issues.append("❌ .env file hiányzik - futtasd a setup.py-t")
    
    # Check if logs directory exists
    if not Path("logs").exists():
        Path("logs").mkdir(exist_ok=True)
        print("📁 Created logs directory")
    
    # Check basic dependencies
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Core dependencies elérhetők")
    except ImportError as e:
        issues.append(f"❌ Hiányzó dependency: {e.name}")
    
    return issues


def run_development():
    """Run in development mode"""
    print("🚀 GarvisNeuralMind indítása fejlesztői módban...")
    
    # Change to src directory and run main.py
    os.chdir("src")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn nincs telepítve")
        return 1
    except Exception as e:
        print(f"❌ Hiba az alkalmazás indítása során: {e}")
        return 1


def run_production():
    """Run in production mode"""
    print("🚀 GarvisNeuralMind indítása production módban...")
    
    try:
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            workers=4,
            log_level="warning"
        )
    except ImportError:
        print("❌ uvicorn nincs telepítve")
        return 1
    except Exception as e:
        print(f"❌ Hiba az alkalmazás indítása során: {e}")
        return 1


def run_docker():
    """Run using Docker Compose"""
    print("🐳 GarvisNeuralMind indítása Docker-rel...")
    
    try:
        # Check if docker-compose is available
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        
        # Start services
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Docker services elindítva")
        print("📊 Logs megtekintése: docker-compose logs -f")
        print("🛑 Leállítás: docker-compose down")
        
    except subprocess.CalledProcessError:
        print("❌ Docker Compose nem elérhető")
        return 1
    except FileNotFoundError:
        print("❌ Docker nincs telepítve")
        return 1


def run_tests():
    """Run tests"""
    print("🧪 Tesztek futtatása...")
    
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)
        print("✅ Minden teszt sikeres")
    except subprocess.CalledProcessError:
        print("❌ Néhány teszt sikertelen")
        return 1
    except FileNotFoundError:
        print("❌ pytest nincs telepítve")
        return 1


def show_status():
    """Show application status"""
    print("📊 GarvisNeuralMind státusz:")
    
    # Check if running locally
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Alkalmazás fut locally (http://localhost:8000)")
        else:
            print("⚠️  Alkalmazás elérhető de válaszol hibával")
    except:
        print("❌ Alkalmazás nem fut locally")
    
    # Check Docker services
    try:
        result = subprocess.run(
            ["docker-compose", "ps"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        if "garvis-app" in result.stdout:
            print("✅ Docker services futnak")
        else:
            print("❌ Docker services nem futnak")
    except:
        print("❌ Docker szolgáltatások nem elérhetők")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="GarvisNeuralMind Runner")
    parser.add_argument(
        "command",
        choices=["dev", "prod", "docker", "test", "status", "check"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    # Always check environment first
    if args.command != "check":
        issues = check_environment()
        if issues:
            print("⚠️  Environment problémák:")
            for issue in issues:
                print(f"  {issue}")
            if args.command != "status":
                print("\n💡 Futtasd: python scripts/setup.py")
                return 1
    
    # Run the requested command
    if args.command == "dev":
        return run_development()
    elif args.command == "prod":
        return run_production()
    elif args.command == "docker":
        return run_docker()
    elif args.command == "test":
        return run_tests()
    elif args.command == "status":
        show_status()
        return 0
    elif args.command == "check":
        issues = check_environment()
        if issues:
            for issue in issues:
                print(issue)
            return 1
        else:
            print("✅ Environment OK")
            return 0
    
    return 0


if __name__ == "__main__":
    exit(main())