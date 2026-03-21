"""Quick script to check if backend is running."""

import requests

def check_backend():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is RUNNING!")
            print(f"   Status: {data.get('status')}")
            print(f"   Ollama: {data.get('ollama')}")
            print(f"   Model: {data.get('model')}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running!")
        print("\nTo start the backend:")
        print("1. Double-click 'start-backend.bat'")
        print("   OR")
        print("2. Open terminal and run:")
        print("   cd backend")
        print("   venv\\Scripts\\activate")
        print("   uvicorn app.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

if __name__ == "__main__":
    print("Checking PathForge Backend...\n")
    check_backend()
