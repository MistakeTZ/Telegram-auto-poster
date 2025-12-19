import asyncio

from generators.config import init_session, setup_logging
from generators.sheduler import main

if __name__ == "__main__":
    setup_logging()
    init_session()
    asyncio.run(main())
