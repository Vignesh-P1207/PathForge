import asyncio
import httpx

async def main():
    # Extract job ID from URL
    url = "https://www.naukri.com/job-listings-data-analyst-capgemini-chennai-delhi-ncr-mumbai-all-areas-4-to-9-years-021225014173"
    import re
    jid_match = re.search(r'-(\d{12,})', url)
    if jid_match:
        jid = jid_match.group(1)
        print(f"Job ID: {jid}")
        api_url = f"https://www.naukri.com/jobapi/v3/job/{jid}"
        print(f"API URL: {api_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "appid": "109",
            "systemid": "Naukri",
            "Referer": url,
        }
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            try:
                resp = await client.get(api_url)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Keys: {list(data.keys())}")
                    # Try different paths
                    desc = data.get("jobDetails", {}).get("description", "")
                    if not desc:
                        desc = data.get("jobDesc", "")
                    if desc:
                        from bs4 import BeautifulSoup
                        clean = BeautifulSoup(desc, "html.parser").get_text(separator="\n", strip=True)
                        print(f"\nDescription ({len(clean)} chars):\n{'='*60}")
                        print(clean[:2000])
                    else:
                        # Print full response to understand structure
                        import json
                        print(json.dumps(data, indent=2)[:3000])
                else:
                    print(f"Response: {resp.text[:500]}")
            except Exception as e:
                print(f"Error: {type(e).__name__}: {e}")

asyncio.run(main())
