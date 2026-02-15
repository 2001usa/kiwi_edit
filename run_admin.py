import uvicorn
import os
import sys

# Ensure the app module is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.web.main:app", host="0.0.0.0", port=port, reload=True)
