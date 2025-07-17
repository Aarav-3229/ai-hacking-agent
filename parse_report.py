import json

with open("report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vulnerabilities = data.get("results", [])
for v in vulnerabilities:
    print("File:", v["path"])
    print("Line:", v["start"]["line"])
    print("Message:", v["extra"]["message"])
    print("Code:", v["extra"].get("lines", "N/A"))
    print("-" * 50)
