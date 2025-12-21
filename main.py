import asyncio

import generators.config  # noqa F401
from generators.sheduler import main

if __name__ == "__main__":
    asyncio.run(main())
