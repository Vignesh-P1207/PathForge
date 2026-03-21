import asyncio
import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}

async def main():
    url = "https://www.naukri.com/job-listings-data-analyst-capgemini-chennai-delhi-ncr-mumbai-all-areas-4-to-9-years-021225014173"
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers={
            **_HEADERS,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.naukri.com/",
        },
    ) as client:
        resp = await client.get(url)
        print(f"Status code: {resp.status_code}")
        with open("naukri_debug.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("HTML saved to naukri_debug.html")

asyncio.run(main())
