import subprocess
import os

def run_git_command(command, cwd="Workspace"):
    """Runs a git command in the given directory."""
    try:
        full_command = f"git {command}"
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            return f"Git Error:\n{result.stderr}"
        return result.stdout.strip() if result.stdout else "Git command executed successfully."
    except Exception as e:
        return f"Git execution exception: {str(e)}"
