import sys
import asyncio
from fastapi import Request

# Mock request class
class MockRequest(Request):
    def __init__(self, json_data):
        self._json = json_data
    async def json(self):
        return self._json

async def test():
    from app.main import generate_report
    req = MockRequest({
        "match_pct": 75,
        "critical_gaps": 2,
        "time_saved_pct": 10,
        "weeks_to_ready": 2,
        "ats": {
            "ats_score": 85,
            "ats_grade": "Good",
            "dimensions": {
                "keyword_match": 80,
                "format_structure": 90,
                "section_coverage": 85,
                "quantification": 70,
                "action_verbs": 90
            },
            "tips": ["Tip 1", "Tip 2"]
        },
        "current_skills": [{"name": "Python", "pct": 90}],
        "required_skills": [{"name": "Go", "pct": 80, "type": "gap"}],
        "pathway": [
            {"week": "WK 01", "title": "Advanced Go", "hrs": "10", "tagLabel": "gap"}
        ]
    })
    
    try:
        res = await generate_report(req)
        print("SUCCESS! Base64 size:", len(res["pdf_base64"]))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
