import urllib.request
import json
import sys

req = urllib.request.Request(
    'http://localhost:8000/api/report',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'match_pct': 0,
        'critical_gaps': 0,
        'time_saved_pct': 0,
        'current_skills': [],
        'required_skills': [],
        'pathway': [],
        'reasoning_trace': [],
        'weeks_to_ready': 4,
        'ats': {}
    }).encode('utf-8')
)

try:
    resp = urllib.request.urlopen(req)
    print("SUCCESS", resp.status)
except urllib.error.HTTPError as e:
    print("HTTPError", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Exception:", e)
