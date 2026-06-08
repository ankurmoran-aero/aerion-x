import os, subprocess
out = subprocess.run(["git", "ls-remote", "https://github.com/ankurmoran-aero/aerion-x.git", "HEAD"], capture_output=True, text=True, check=True)
latest_sha = out.stdout.split()[0]

sha_file = os.path.expanduser("~/.aerion-x/.commit_sha")
current_sha = ""
if os.path.exists(sha_file):
    with open(sha_file, "r") as f:
        current_sha = f.read().strip()
        
print(f"Latest: '{latest_sha}'")
print(f"Current: '{current_sha}'")
print(latest_sha != current_sha)
