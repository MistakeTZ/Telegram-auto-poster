import asyncio

from generators.config import setup_logging
from generators.sheduler import main

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
