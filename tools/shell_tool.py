import subprocess
import os
import shutil
from rich.console import Console

console = Console()

def run_shell(command, cli_name="BrahMos", cwd="Workspace", auto_approve=False):
    """Executes a shell command. If auto_approve is True, skips the confirmation prompt."""
    if not auto_approve:
        console.print(f"\n[bold yellow]\\[!] {cli_name} wants to execute:[/bold yellow] [white]{command}[/white]")
        try:
            confirm = console.input("[bold green]Authorize execution? (y/n): [/bold green]").lower()
        except EOFError:
            return "Error: Received EOF when waiting for confirmation. Use auto_approve if running non-interactively."
        
        if confirm != 'y':
            return "Command execution cancelled by user."
    
    try:
        # Ensure cwd exists
        os.makedirs(cwd, exist_ok=True)
        
        # Dynamically find the best shell
        shell_path = shutil.which("bash") or shutil.which("sh") or os.environ.get("SHELL")
        
        # Execute command
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120, executable=shell_path, cwd=cwd)
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"
