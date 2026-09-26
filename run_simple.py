import uvicorn
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Civic Task Navigator on http://127.0.0.1:{port}")
    uvicorn.run("simple_app.main:app", host="127.0.0.1", port=port, reload=False)
