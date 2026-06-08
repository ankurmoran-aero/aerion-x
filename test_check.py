import os, subprocess, sys
def check_for_updates():
    try:
        if os.environ.get("AERION_SKIP_UPDATE"):
            return
        import subprocess, sys, os
        print("[*] Checking for Aerion-X updates...")
        
        out = subprocess.run(["git", "ls-remote", "https://github.com/ankurmoran-aero/aerion-x.git", "HEAD"], capture_output=True, text=True, check=True)
        latest_sha = out.stdout.split()[0]
        
        sha_file = os.path.expanduser("~/.aerion-x/.commit_sha")
        current_sha = ""
        if os.path.exists(sha_file):
            with open(sha_file, "r") as f:
                current_sha = f.read().strip()
                
        if latest_sha != current_sha:
            print("[*] Update found! Downloading latest version...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            if os.path.exists(os.path.join(script_dir, ".git")):
                subprocess.run(["git", "pull"], cwd=script_dir, capture_output=True, check=True)
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/ankurmoran-aero/aerion-x.git"], capture_output=True, check=True)
                
            os.makedirs(os.path.expanduser("~/.aerion-x"), exist_ok=True)
            with open(sha_file, "w") as f:
                f.write(latest_sha)
                
            print("[*] Update successful. Restarting Aerion-X...\n")
            os.environ["AERION_SKIP_UPDATE"] = "1"
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"Error: {e}")
check_for_updates()
