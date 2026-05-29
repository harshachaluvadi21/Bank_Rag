import urllib.request
import json
import urllib.error

print("Testing /api/health...")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/health")
    with urllib.request.urlopen(req) as response:
        print("Health status code:", response.getcode())
        print(json.dumps(json.loads(response.read().decode()), indent=2))
except Exception as e:
    print("Health test failed:", e)

print("\nTesting /api/chat...")
try:
    data = json.dumps({"query": "What is repo rate?", "conversation_id": "abc123", "history": []}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/chat", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        print("Chat status code:", response.getcode())
        print(json.dumps(json.loads(response.read().decode()), indent=2))
except urllib.error.HTTPError as e:
    print("Chat HTTPError:", e.code, e.read().decode())
except Exception as e:
    print("Chat test failed:", e)
