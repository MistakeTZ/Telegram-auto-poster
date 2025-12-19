import asyncio
import logging
from datetime import datetime, timedelta
from os import getenv
from sys import argv

from generators.sender import send_article


async def main():
    if "send_now" in argv:
        logging.info("Sending article now")
        await send_article(datetime.now())

    else:
        food_times = {}
        send_times = []
        for time in ["breakfast", "launch", "dinner"]:
            times = [int(time) for time in getenv(time).split(",")]
            food_times[time] = times
            send_times = send_times + times

        logging.info(send_times)

        while True:
            now = datetime.now()
            current_hour = now.hour

            future_hours_today = [h for h in send_times if h > current_hour]

            if future_hours_today:
                next_hour = future_hours_today[0]
                next_day_offset = 0
            else:
                next_hour = send_times[0]
                next_day_offset = 1

            for key in food_times:
                if next_hour in food_times[key]:
                    break

            target_time = datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=next_hour,
                minute=0,
                second=0,
                microsecond=0,
            )

            target_time += timedelta(days=next_day_offset)

            if target_time <= now:
                target_time += timedelta(days=1)
                target_time = target_time.replace(hour=send_times[0])

            wait_seconds = (target_time - timedelta(minutes=5) - now).total_seconds()
            if wait_seconds < 0:
                wait_seconds = 0

            logging.info(
                f"Next send scheduled for {target_time} (in {wait_seconds:.0f} seconds)"
            )

            if "debug" in argv:
                logging.info("Prepared to send article")
                return
            else:
                await asyncio.sleep(wait_seconds)

                await send_article(target_time, key)
