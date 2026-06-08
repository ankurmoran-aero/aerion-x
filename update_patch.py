import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Update check_for_updates
old_check = """def check_for_updates():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(os.path.join(script_dir, ".git")):
            return
            
        if os.environ.get("AERION_SKIP_UPDATE"):
            return

        print("[*] Checking for Aerion-X updates...")
        subprocess.run(["git", "fetch"], cwd=script_dir, capture_output=True, check=True)
        status = subprocess.run(["git", "status", "-uno"], cwd=script_dir, capture_output=True, text=True).stdout
        
        if "Your branch is behind" in status:
            print("[*] Update found. Downloading latest version...")
            subprocess.run(["git", "pull"], cwd=script_dir, capture_output=True, check=True)
            print("[*] Update successful. Restarting Aerion-X...\\n")
            
            os.environ["AERION_SKIP_UPDATE"] = "1"
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        pass # Silently fail if git update doesn't work (e.g., offline)"""

new_check = """def check_for_updates():
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
                
            print("[*] Update successful. Restarting Aerion-X...\\n")
            os.environ["AERION_SKIP_UPDATE"] = "1"
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        pass # Silently fail if offline or error"""

content = content.replace(old_check, new_check)

# 2. Update the prompt to remove BrahMosCloud
old_prompt = """choice = console.input("[bold cyan]Do you have the official Aerion-X / BrahMosCloud API Key? (y/n): [/bold cyan]").strip().lower()"""
new_prompt = """choice = console.input("[bold cyan]Do you have the official Aerion-X API Key? (y/n): [/bold cyan]").strip().lower()"""

content = content.replace(old_prompt, new_prompt)

with open("main.py", "w") as f:
    f.write(content)
