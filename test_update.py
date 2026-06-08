import subprocess, sys, os
out = subprocess.run(["git", "ls-remote", "https://github.com/ankurmoran-aero/aerion-x.git", "HEAD"], capture_output=True, text=True, check=True)
latest_sha = out.stdout.split()[0]
print(latest_sha)
