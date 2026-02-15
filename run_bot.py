import asyncio
import sys
import os

# Ensure the app module is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.bot.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
