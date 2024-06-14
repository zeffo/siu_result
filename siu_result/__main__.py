import asyncio
import sys
import time

from playwright.async_api import async_playwright

from siu_result import Scraper


def parse_args():
    try:
        prn, seat, out = sys.argv[1:]
        return prn, seat, out
    except ValueError:
        raise ValueError(
            "Please pass the PRN, Seat Number and Output path to the command."
        )


async def main():
    prn, seat, out = parse_args()
    start = time.perf_counter()
    print("Fetching data...")
    async with async_playwright() as playwright:
        async with Scraper(playwright, playwright.firefox) as scraper:
            await scraper.run(prn, seat, out)
    end = time.perf_counter()
    print(f"Finished in {end-start}s.")


asyncio.run(main())
