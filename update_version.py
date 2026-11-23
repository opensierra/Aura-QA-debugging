import subprocess, json, datetime, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

commit = subprocess.check_output(["git", "log", "-1", "--format=%h"]).decode().strip()
now = datetime.datetime.now()
date = now.strftime("%Y%m%d")
time = now.strftime("%H%M")

data = {"version": "1.4.9", "commit": commit, "date": date, "time": time}

with open("UI/version.json", "w") as f:
    json.dump(data, f)

print(f"version.json updated: {commit} {date}")
