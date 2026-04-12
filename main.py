import json
import sys
import os
import subprocess
import platform
import shutil
from datetime import datetime

# --- Auto-Install Dependencies ---
def ensure_dependencies():
    required = ["colorama", "requests", "beautifulsoup4", "googlesearch-python", "rich"]
    for pkg in required:
        # Map package name to import name
        import_name = "bs4" if pkg == "beautifulsoup4" else "googlesearch" if pkg == "googlesearch-python" else pkg
        try:
            __import__(import_name)
        except ImportError:
            print(f"[!] Installing required package: {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)

ensure_dependencies()

# --- Third-Party Imports (Safe to import now) ---
import requests
from colorama import Fore, Style, init
init(autoreset=True)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
console = Console()

# Import modular tools AFTER dependencies are installed
from tools.shell_tool import run_shell
from tools.file_tool import list_files, read_file, write_file
from tools.web_tool import google_search, web_browse
from tools.plan_tool import discuss_and_plan
from tools.input_tool import ask_user_input

from config import MODEL_API_URL, MODEL_API_KEY, MODEL_NAME, SYSTEM_PROMPT, CLI_NAME, DEVELOPER, VERSION

# --- UI Helpers (RICH MODERN EDITION) ---

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    logo = """[bold magenta]
██████╗ ██████╗  █████╗ ██╗  ██╗███╗   ███╗ ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗██║  ██║████╗ ████║██╔═══██╗██╔════╝
██████╔╝██████╔╝███████║███████║██╔████╔██║██║   ██║███████╗
██╔══██╗██╔══██╗██╔══██║██╔══██║██║╚██╔╝██║██║   ██║╚════██║
██████╔╝██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
[/bold magenta]"""
    
    credits_line = f" [white]Made By Ankur Moran[/white]  |  [magenta]TG:[/magenta] [white]@Ankxrrrr[/white]  |  [magenta]IG:[/magenta] [white]_ankurmoran_[/white] "
    version_line = f" [dim]CLI Version: {VERSION}  |  Engine: {MODEL_NAME}[/dim]"
    
    panel = Panel(
        f"{logo}\n{credits_line}\n{version_line}",
        border_style="purple",
        expand=False,
        padding=(1, 4)
    )
    console.print(panel)

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log_brahmos(msg):
    if not msg:
        return
    md = Markdown(msg, justify="left")
    panel = Panel(md, title="[bold magenta]BrahMos[/bold magenta]", title_align="left", border_style="purple", expand=True)
    console.print()
    console.print(panel)
    console.print()

def log_tool(msg):
    console.print(f"[bold purple]│ ⚙ TOOL:[/bold purple] [white]{msg}[/white]")

def log_error(msg):
    console.print(f"[bold red]│ ✖ ERROR:[/bold red] [white]{msg}[/white]")

# --- OS Detection ---
def get_os_info():
    try:
        distro = "Unknown"
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].lower().replace('"', '')
        elif "termux" in sys.prefix:
            distro = "termux"
        return f"OS: {platform.system()}, Distro: {distro}, Machine: {platform.machine()}"
    except:
        return "OS: Linux (Unknown Distro)"

# Mapping tool names to functions (using modular imports)

# Global state for current working directory
current_working_dir = "Workspace"

def change_directory(path):
    global current_working_dir
    # Handle absolute and relative paths
    new_path = os.path.abspath(os.path.join(current_working_dir, path)) if not os.path.isabs(path) else path
    if os.path.isdir(new_path):
        current_working_dir = new_path
        return f"Successfully changed directory to {current_working_dir}"
    else:
        return f"Error: Directory not found: {new_path}"

TOOLS = {
    "run_shell": lambda command: run_shell(command, CLI_NAME, cwd=current_working_dir),
    "list_files": lambda path=None: list_files(path if path else current_working_dir),
    "read_file": lambda file_path: read_file(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path),
    "write_file": lambda file_path, content: write_file(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path, content),
    "change_directory": change_directory,
    "google_search": google_search,
    "web_browse": web_browse,
    "discuss_and_plan": discuss_and_plan,
    "ask_user_input": ask_user_input
}

# --- API Interaction ---
def get_brahmos_response(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MODEL_API_KEY}",
        "HTTP-Referer": "https://github.com/ankurmoran96-openai/brahmos",
        "X-Title": "BrahMos"
    }

    tools_config = [
        {"type": "function", "function": {"name": "google_search", "description": "Search the live web for real-time info.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
        {"type": "function", "function": {"name": "web_browse", "description": "Read content from a URL.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
        {"type": "function", "function": {"name": "run_shell", "description": "Run any shell command.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
        {"type": "function", "function": {"name": "list_files", "description": "List directory contents.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Optional path. Defaults to current working directory."}}}}},
        {"type": "function", "function": {"name": "read_file", "description": "Read file contents.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
        {"type": "function", "function": {"name": "write_file", "description": "Create/update files.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}},
        {"type": "function", "function": {"name": "change_directory", "description": "Change the current working directory for the AI. Use this when the user gives you access to a different folder.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "The path to change to."}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "discuss_and_plan", "description": "Enter an interactive chat with the user using gpt-4o to brainstorm and plan a project. Returns the final blueprint.", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Optional initial topic to discuss"}}, "required": []}}},
        {"type": "function", "function": {"name": "ask_user_input", "description": "Ask the user for specific input, such as a missing API key, token, password, or setting. If it is a secret (like a password or token), set is_secret to true so the user's input is hidden.", "parameters": {"type": "object", "properties": {"prompt_message": {"type": "string", "description": "The question or prompt to show the user."}, "is_secret": {"type": "boolean", "description": "Set to true if asking for a password/token to hide their typing."}}, "required": ["prompt_message"]}}}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": tools_config,
        "tool_choice": "auto",
        "temperature": 0.2
    }
    
    try:
        resp = requests.post(MODEL_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        
        try:
            return resp.json()["choices"][0]["message"]
        except (KeyError, json.JSONDecodeError) as e:
            return {"role": "assistant", "content": f"BrahMos API Error: Unexpected response format: {resp.text[:200]}"}
            
    except Exception as e:
        return {"role": "assistant", "content": f"BrahMos API Error: {str(e)}"}

def main():
    os_info = get_os_info()
    os.makedirs("Workspace", exist_ok=True)
    
    print_banner()
    console.print(f" [purple]├─[/purple] [white]System:[/white] {os_info}")
    console.print(f" [purple]├─[/purple] [white]Location:[/white] {os.path.abspath(current_working_dir)}")
    console.print(f" [purple]└─[/purple] [white]Status:[/white] [bold magenta]Active & Awaiting Directives[/bold magenta]\n")
    
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\nENV: {os_info}"}]
    
    while True:
        try:
            prompt = f"\n[bold magenta]╭─ You[/bold magenta] [dim]({os.path.basename(os.path.abspath(current_working_dir))})[/dim]\n[bold magenta]╰─❯ [/bold magenta]"
            user_input = console.input(prompt)
            
            if user_input.lower() in ["exit", "quit", "clear"]:
                if user_input.lower() == "clear":
                    os.system('clear')
                    print_banner()
                    console.print(f" [purple]├─[/purple] [white]System:[/white] {os_info}")
                    console.print(f" [purple]├─[/purple] [white]Location:[/white] {os.path.abspath(current_working_dir)}")
                    console.print(f" [purple]└─[/purple] [white]Status:[/white] [bold magenta]Active & Awaiting Directives[/bold magenta]\n")
                    continue
                break
                
            if user_input.lower().startswith("cd ") or user_input.lower().startswith("/cd "):
                # Quick manual cd command for the user
                new_path = user_input.split(" ", 1)[1].strip()
                res = change_directory(new_path)
                console.print(f"[bold purple]│[/bold purple] {res}")
                continue

            if user_input.lower() in ["/shell", "shell"]:
                console.print("\n[bold purple]╭───────────────────────────────────────────────────╮[/bold purple]")
                console.print(f"[bold purple]│[/bold purple] [bold white]Entering Interactive Shell...[/bold white]                     [bold purple]│[/bold purple]")
                console.print(f"[bold purple]│[/bold purple] [white]Location: {os.path.abspath(current_working_dir)[:35]:<35}[/white] [bold purple]│[/bold purple]")
                console.print("[bold purple]│[/bold purple] [bold white]Type 'exit' or press Ctrl+D to return to BrahMos.[/bold white] [bold purple]│[/bold purple]")
                console.print("[bold purple]╰───────────────────────────────────────────────────╯[/bold purple]\n")
                
                cwd = os.getcwd()
                os.chdir(current_working_dir)
                shell_exec = shutil.which("bash") or shutil.which("sh") or os.environ.get("SHELL", "sh")
                os.system(shell_exec)
                os.chdir(cwd)
                
                console.print("\n[bold magenta]Returned to BrahMos. Awaiting Directives.[/bold magenta]")
                continue
            
            if user_input.lower().startswith("/model"):
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    new_model = parts[1].strip()
                    global MODEL_NAME
                    MODEL_NAME = new_model
                    console.print(f"[bold purple]│[/bold purple] [green]Model switched to {MODEL_NAME}[/green]")
                else:
                    from config import AVAILABLE_MODELS
                    console.print("[bold purple]│[/bold purple] Available models:")
                    console.print(f"[bold purple]│[/bold purple] Free: {', '.join(AVAILABLE_MODELS['free'])}")
                    console.print(f"[bold purple]│[/bold purple] Paid: {', '.join(AVAILABLE_MODELS['paid'])}")
                    console.print(f"[bold purple]│[/bold purple] Current: {MODEL_NAME}")
                continue

            if not user_input.strip():
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            turn_count = 0
            max_turns = 10
            
            with console.status("[bold purple]...processing...[/bold purple]", spinner="dots") as status:
                while turn_count < max_turns:
                    turn_count += 1
                    response = get_brahmos_response(messages)
                    messages.append(response)
                    
                    if response.get("content"):
                        status.stop()
                        log_brahmos(response["content"])
                        status.start()
                    
                    if "tool_calls" in response and response["tool_calls"]:
                        for tool_call in response["tool_calls"]:
                            func_name = tool_call["function"]["name"]
                            
                            try:
                                args = json.loads(tool_call["function"]["arguments"])
                            except Exception as e:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "name": func_name,
                                    "content": f"Error parsing arguments: {str(e)}"
                                })
                                continue
                            
                            status.stop()
                            log_tool(f"Executing {func_name}...")
                            tool_func = TOOLS.get(func_name)
                            if tool_func:
                                result = tool_func(**args)
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "name": func_name,
                                    "content": str(result)
                                })
                            else:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "name": func_name,
                                    "content": f"Error: Tool {func_name} not found."
                                })
                            status.start()
                        continue
                    else:
                        break
                
                if turn_count >= max_turns:
                    log_error("Maximum autonomous turns reached. Pausing for safety.")
            
        except KeyboardInterrupt:
            console.print(f"\n[bold red]Safe shutdown initiated.[/bold red]")
            break
        except Exception as e:
            log_error(str(e))

if __name__ == "__main__":
    main()
