import asyncio
import httpx
import json

async def main():
    job_id = "021225014173"
    api_url = f"https://www.naukri.com/jobapi/v3/job/{job_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "appid": "109",
        "systemid": "109"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(api_url, headers=headers)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            print("Title:", data.get('jobDetails', {}).get('title'))
            with open("naukri_api_resp.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Saved to naukri_api_resp.json")
        except Exception as e:
            print("Error parsing JSON:", e)
            print(resp.text[:500])

asyncio.run(main())
