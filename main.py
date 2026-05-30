import json
import sys
import os
import subprocess
import platform
import shutil
from datetime import datetime

# --- Auto-Update System ---
def check_for_updates():
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
            print("[*] Update successful. Restarting Aerion-X...\n")
            
            os.environ["AERION_SKIP_UPDATE"] = "1"
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        pass # Silently fail if git update doesn't work (e.g., offline)

check_for_updates()

# --- Auto-Install Dependencies ---
def ensure_dependencies():
    required = ["colorama", "requests", "beautifulsoup4", "googlesearch-python", "rich", "python-dotenv", "prompt_toolkit"]
    for pkg in required:
        import_name = "bs4" if pkg == "beautifulsoup4" else "googlesearch" if pkg == "googlesearch-python" else pkg
        try:
            __import__(import_name)
        except ImportError:
            print(f"[!] Installing required package: {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)

ensure_dependencies()

# --- Third-Party Imports ---
import requests
from colorama import Fore, Style, init
init(autoreset=True)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
console = Console()

# --- Autocomplete ---
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PTStyle


# Import modular tools
from tools.shell_tool import run_shell
from tools.file_tool import list_files, read_file, write_file, replace_text, search_directory
from tools.git_tool import run_git_command
from tools.web_tool import google_search, web_browse
from tools.plan_tool import discuss_and_plan
from tools.input_tool import ask_user_input
from tools.validation_tool import validate_code

from config import MODEL_API_URL, MODEL_API_KEY, MODEL_NAME, THINKER_PROMPT, CODER_PROMPT, DEBUGGER_PROMPT, CLI_NAME, DEVELOPER, VERSION

# --- Theme Management ---
THEMES = {
    "cyan": {"primary": "cyan", "secondary": "purple", "accent": "white"},
    "ocean": {"primary": "blue", "secondary": "cyan", "accent": "white"},
    "forest": {"primary": "green", "secondary": "yellow", "accent": "white"},
    "sunset": {"primary": "orange3", "secondary": "red", "accent": "white"},
    "cyberpunk": {"primary": "magenta", "secondary": "yellow", "accent": "cyan"},
    "ghost": {"primary": "bright_black", "secondary": "white", "accent": "bright_white"}
}
current_theme = THEMES["cyan"]

def set_theme(name):
    global current_theme
    if name in THEMES:
        current_theme = THEMES[name]
        return True
    return False

# --- UI Helpers ---
def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    from rich.table import Table
    from rich.align import Align
    p = current_theme["primary"]
    s = current_theme["secondary"]
    
    logo = f"[bold {p}]" + """
 ⬡ █████╗ ███████╗██████╗ ██╗ ██████╗ ███╗   ██╗     ██╗  ██╗ ⬡
  ██╔══██╗██╔════╝██╔══██╗██║██╔═══██╗████╗  ██║     ╚██╗██╔╝  
  ███████║█████╗  ██████╔╝██║██║   ██║██╔██╗ ██║█████╗╚███╔╝   
  ██╔══██║██╔══╝  ██╔══██╗██║██║   ██║██║╚██╗██║╚════╝██╔██╗   
  ██║  ██║███████╗██║  ██║██║╚██████╔╝██║ ╚████║     ██╔╝ ██╗  
  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═╝  ╚═╝  
""" + f"[/bold {p}]"
    
    table = Table(show_header=False, expand=True, border_style=s, box=None)
    table.add_column("Left", justify="left", ratio=1)
    table.add_column("Right", justify="right", ratio=1)
    
    table.add_row(
        f"[{p}]Architect:[/{p}] [white]Ankur Moran[/white]",
        f"[{s}]Version:[/{s}] [bold white]v6.0.0-PRO[/bold white]"
    )
    table.add_row(
        f"[{p}]Network:[/{p}] [white]BrahMos Cloud[/white]",
        f"[{s}]Engine:[/{s}] [bold white]{MODEL_NAME}[/bold white]"
    )
    
    from rich.console import Group
    panel = Panel(
        Group(Align.center(logo), "", table),
        border_style=p,
        expand=True,
        title=f"[bold {s}]A E R I O N - X[/bold {s}]",
        title_align="center"
    )
    console.print(panel)

def log_aerion_x(msg, title="Aerion-X AI"):
    if not msg:
        return
    import time
    from rich.live import Live
    p = current_theme["primary"]
    
    buffer = ""
    # Smooth animated typewriter effect
    with Live(Panel(Markdown(""), title=f"[bold {p}]{title}[/bold {p}]", title_align="left", border_style=p, expand=True), refresh_per_second=60) as live:
        chunk_size = 4
        for i in range(0, len(msg), chunk_size):
            buffer += msg[i:i+chunk_size]
            live.update(Panel(Markdown(buffer), title=f"[bold {p}]{title}[/bold {p}]", title_align="left", border_style=p, expand=True))
            time.sleep(0.005)
    console.print()

def log_tool(msg):
    p = current_theme["primary"]
    console.print(f"[bold {p}]│ ⚙ TOOL:[/bold {p}] [white]{msg}[/white]")

def log_error(msg):
    console.print(f"[bold red]│ ✖ ERROR:[/bold red] [white]{msg}[/white]")

# --- OS Detection ---
def get_os_info():
    try:
        # Distro Detection
        distro = "Unknown"
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].lower().replace('"', '')
        elif "termux" in sys.prefix:
            distro = "termux"
        
        # CPU Info
        cpu_count = os.cpu_count()
        
        # RAM Info (Linux specific)
        ram_gb = "Unknown"
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        ram_kb = int(line.split()[1])
                        ram_gb = round(ram_kb / (1024 * 1024), 2)
                        break
        
        # Disk Info
        usage = shutil.disk_usage("/")
        disk_free = round(usage.free / (1024**3), 2)
        disk_total = round(usage.total / (1024**3), 2)

        is_root = os.getuid() == 0
        root_status = " (ROOT)" if is_root else ""
        
        specs = f"OS: {platform.system()} | Distro: {distro} | CPU: {cpu_count} Cores | RAM: {ram_gb}GB | Disk: {disk_free}/{disk_total}GB Free{root_status}"
        return specs
    except:
        return "OS: Linux (Unknown Specs)"

current_working_dir = "Workspace"

def change_directory(path):
    global current_working_dir
    new_path = os.path.abspath(os.path.join(current_working_dir, path)) if not os.path.isabs(path) else path
    if os.path.isdir(new_path):
        current_working_dir = new_path
        return f"Successfully changed directory to {current_working_dir}"
    else:
        return f"Error: Directory not found: {new_path}"

TOOLS = {
    "run_shell": lambda command: run_shell(command, CLI_NAME, cwd=current_working_dir, auto_approve=True),
    "list_files": lambda path=None: list_files(path if path else current_working_dir),
    "search_directory": lambda query, path=None: search_directory(query, path if path else current_working_dir),
    "run_git_command": lambda command: run_git_command(command, cwd=current_working_dir),
    "read_file": lambda file_path, start_line=None, end_line=None: read_file(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path, start_line, end_line),
    "write_file": lambda file_path, content: write_file(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path, content),
    "replace_text": lambda file_path, old_string, new_string, allow_multiple=False: replace_text(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path, old_string, new_string, allow_multiple),
    "validate_code": lambda file_path: validate_code(os.path.join(current_working_dir, file_path) if not os.path.isabs(file_path) else file_path),
    "change_directory": change_directory,
    "google_search": google_search,
    "web_browse": web_browse,
    "discuss_and_plan": discuss_and_plan,
    "ask_user_input": ask_user_input
}

def trim_messages(messages, max_tokens=100000):
    total_chars = sum(len(str(m)) for m in messages)
    if total_chars < max_tokens * 4:
        return messages

    log_tool("Context threshold reached. Optimizing history...")
    system_msg = messages[0]
    recent_count = 15
    if len(messages) > recent_count + 1:
        pruned_count = len(messages) - recent_count - 1
        recent = messages[-recent_count:]
        messages.clear()
        messages.append(system_msg)
        messages.append({"role": "system", "content": f"[System: {pruned_count} older messages have been pruned to optimize context window.]"})
        messages.extend(recent)
    return messages

# --- Session Analytics ---
total_tokens_used = 0
total_tools_executed = 0

# --- API Interaction ---
def get_aerion_x_response(messages, use_tools=True, stream_callback=None):
    global total_tokens_used
    messages = trim_messages(messages)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.MODEL_API_KEY}",
        "HTTP-Referer": "https://github.com/ankurmoran-aero/aerion-x",
        "X-Title": "Aerion-X"
    }

    payload = {"model": config.MODEL_NAME, "messages": messages, "temperature": 0.2}
    
    if use_tools:
        tools_config = [
            {"type": "function", "function": {"name": "google_search", "description": "Search the live web.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "web_browse", "description": "Read a URL.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
            {"type": "function", "function": {"name": "run_shell", "description": "Run shell command.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
            {"type": "function", "function": {"name": "list_files", "description": "List files.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}},
            {"type": "function", "function": {"name": "search_directory", "description": "Search for files.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "read_file", "description": "Read file with range.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}, "required": ["file_path"]}}},
            {"type": "function", "function": {"name": "write_file", "description": "Write file.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]}}},
            {"type": "function", "function": {"name": "replace_text", "description": "Replace text in file.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}}, "required": ["file_path", "old_string", "new_string"]}}},
            {"type": "function", "function": {"name": "validate_code", "description": "Check syntax.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
            {"type": "function", "function": {"name": "change_directory", "description": "Change CWD.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}}
        ]
        payload["tools"] = tools_config
        payload["tool_choice"] = "auto"
    
    if stream_callback:
        payload["stream"] = True

    try:
        resp = requests.post(config.MODEL_API_URL, headers=headers, json=payload, timeout=60, stream=bool(stream_callback))
        resp.raise_for_status()
        
        if stream_callback:
            full_content = ""
            tool_calls = {}
            for line in resp.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]": break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    full_content += delta["content"]
                                    stream_callback(delta["content"], full_content)
                                
                                if "tool_calls" in delta:
                                    for tc in delta["tool_calls"]:
                                        idx = tc.get("index")
                                        if idx not in tool_calls:
                                            tool_calls[idx] = {"id": tc.get("id"), "type": "function", "function": {"name": "", "arguments": ""}}
                                        if "function" in tc:
                                            if "name" in tc["function"] and tc["function"]["name"]:
                                                tool_calls[idx]["function"]["name"] += tc["function"]["name"]
                                            if "arguments" in tc["function"] and tc["function"]["arguments"]:
                                                tool_calls[idx]["function"]["arguments"] += tc["function"]["arguments"]
                        except json.JSONDecodeError:
                            pass
            
            # Assemble final message
            final_message = {"role": "assistant"}
            if full_content:
                final_message["content"] = full_content
            if tool_calls:
                final_message["tool_calls"] = list(tool_calls.values())
            
            total_tokens_used += int(len(full_content) / 4) # Approximation
            return final_message
        else:
            data = resp.json()
            if "usage" in data:
                total_tokens_used += data["usage"].get("total_tokens", 0)
            return data["choices"][0]["message"]
    except Exception as e:
        return {"role": "assistant", "content": f"Aerion-X API Error: {str(e)}"}

def generate_layout():
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=6),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="chat", ratio=2),
        Layout(name="agents", ratio=1)
    )
    layout["agents"].split_column(
        Layout(name="thinker", ratio=1),
        Layout(name="coder", ratio=1),
        Layout(name="watchdog", ratio=1)
    )
    return layout

SESSION_DIR = os.path.expanduser("~/.aerion-x/sessions")

def list_sessions():
    if not os.path.exists(SESSION_DIR): return []
    files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(SESSION_DIR, x)), reverse=True)
    return [f.replace(".json", "") for f in files]

def load_session(session_id):
    session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(session_file):
        with open(session_file, 'r') as f: return json.load(f)
    return None

def save_session(session_id, messages):
    os.makedirs(SESSION_DIR, exist_ok=True)
    with open(os.path.join(SESSION_DIR, f"{session_id}.json"), 'w') as f: json.dump(messages, f, indent=4)

def main():
    global total_tokens_used, total_tools_executed
    os_info = get_os_info()
    os.makedirs("Workspace", exist_ok=True)
    
    import config
    import sys
    if not config.MODEL_API_KEY:
        print_banner()
        console.print("[bold yellow]Welcome to Aerion-X CLI![/bold yellow]")
        choice = console.input("[bold cyan]Do you have the official Aerion-X / BrahMosCloud API Key? (y/n): [/bold cyan]").strip().lower()
        
        os.makedirs(config.AERION_X_DIR, exist_ok=True)
        
        if choice in ['y', 'yes']:
            try:
                api_key = console.input("[bold green]Enter Official API Key: [/bold green]").strip()
            except EOFError:
                api_key = ""
                
            if api_key:
                with open(config.GLOBAL_ENV_FILE, "a") as f:
                    f.write(f"\nMODEL_API_KEY={api_key}\n")
                config.MODEL_API_KEY = api_key
                console.print("[bold green]✔ Official API Key saved![/bold green]\n")
            else:
                console.print("[bold red]Error: API Key is required.[/bold red]")
                sys.exit(1)
        else:
            console.print("\n[bold yellow]Custom API Setup[/bold yellow]")
            try:
                api_url = console.input("[white]Enter API URL Endpoint (e.g., https://api.openai.com/v1/chat/completions): [/white]").strip()
                api_model = console.input("[white]Enter Model Name (e.g., gpt-4o): [/white]").strip()
                api_key = console.input("[white]Enter API Key: [/white]").strip()
            except EOFError:
                api_url = api_model = api_key = ""
                
            if api_url and api_model and api_key:
                with open(config.GLOBAL_ENV_FILE, "a") as f:
                    f.write(f"\nMODEL_API_URL={api_url}\nMODEL_NAME={api_model}\nMODEL_API_KEY={api_key}\n")
                config.MODEL_API_URL = api_url
                config.MODEL_NAME = api_model
                config.MODEL_API_KEY = api_key
                console.print("[bold green]✔ Custom API Setup saved![/bold green]\n")
            else:
                console.print("[bold red]Error: All fields are required for custom setup.[/bold red]")
                sys.exit(1)
    
    print_banner()
    p = current_theme["primary"]
    s = current_theme["secondary"]
    console.print(f" [{s}]├─[/{s}] [white]System:[/white] {os_info}")
    console.print(f" [{s}]├─[/{s}] [white]Location:[/white] {os.path.abspath(current_working_dir)}")
    
    base_env_message = {"role": "user", "content": f"[SYSTEM ENV INFO]\n{os_info}\nCurrent CWD: {os.path.abspath(current_working_dir)}"}
    messages = [base_env_message]
    sessions = list_sessions()
    current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if sessions:
        latest_session_id = sessions[0]
        previous_session = load_session(latest_session_id)
        if previous_session:
            console.print(f" [{s}]├─[/{s}] [white]Session:[/white] [green]Previous session found.[/green]")
            prompt = f"\n[bold {p}]?[/bold {p}] Resume session? (Y/n): "
            if console.input(prompt).strip().lower() in ['', 'y', 'yes']:
                messages = previous_session
                current_session_id = latest_session_id
    
    while True:
        try:
            p = current_theme["primary"]
            s = current_theme["secondary"]
            cwd_name = os.path.basename(os.path.abspath(current_working_dir))
            
            try:
                console.print(f"\n[bold {p}]╭─ You[/bold {p}] [dim]({cwd_name})[/dim]")
                slash_commands = ['/help', '/conf', '/theme', '/model', '/cd', '/btw', '/history', '/export', '/rollback', '/summary', '/system', '/tokens', '/exit', '/clear']
                cmd_completer = WordCompleter(slash_commands, ignore_case=True, match_middle=False)
                
                # We use prompt_toolkit so autocomplete drops down menus when typing /
                user_input = pt_prompt("╰─❯ ", completer=cmd_completer)
            except EOFError:
                user_input = "/exit"
            
            cmd = user_input.lower().split()[0] if user_input.strip() else ""
            
            if cmd in ["exit", "quit", "/exit"]:
                p = current_theme["primary"]
                console.print(f"\n[bold {p}]╭─ Session Analytics ────────────╮[/bold {p}]")
                console.print(f"[bold {p}]│[/bold {p}] [white]Total Tokens:[/white] {total_tokens_used:,}")
                console.print(f"[bold {p}]│[/bold {p}] [white]Tools Executed:[/white] {total_tools_executed}")
                console.print(f"[bold {p}]│[/bold {p}] [white]Session ID:[/white] {current_session_id}")
                console.print(f"[bold {p}]╰──────────────────────────────╯[/bold {p}]")
                console.print(f"\n[bold green]✔[/bold green] [white]Aerion-X session saved. Goodbye![/white]\n")
                break

            elif cmd == "clear" or cmd == "/clear":
                print_banner()
                continue

            elif cmd in ["/help", "help"]:
                from rich.table import Table
                table = Table(box=None, show_header=False, expand=True)
                table.add_column("Command", style=f"bold {p}", width=18)
                table.add_column("Description", style="white")
                table.add_row("/help", "Show this command directory")
                table.add_row("/conf", "Configure your API Key and endpoint URLs")
                table.add_row("/theme <name>", f"Switch visual aesthetics ({', '.join(THEMES.keys())})")
                table.add_row("/model <name>", "Swap out the underlying LLM engine")
                table.add_row("/cd <path>", "Navigate the filesystem (Workspace scope)")
                table.add_row("/btw <msg>", "Inject background context without triggering the AI immediately")
                table.add_row("/history", "View the current session's message history log")
                table.add_row("/export <file>", "Export the current session to a Markdown file")
                table.add_row("/rollback", "Undo the last prompt and AI response")
                table.add_row("/summary", "View deep analytics on the current session")
                table.add_row("/system", "View target device hardware specifications")
                table.add_row("/tokens", "View live token burn metrics")
                table.add_row("clear", "Wipe terminal and reset the HUD")
                table.add_row("exit", "Terminate connection to BrahMos Cloud")
                console.print(Panel(table, title=f"[bold {p}]COMMAND DIRECTORY[/bold {p}]", title_align="left", border_style=p))
                continue

            elif cmd == "/theme":
                parts = user_input.split(" ", 1)
                if len(parts) > 1 and set_theme(parts[1].strip().lower()):
                    console.print(f"[bold green]✔[/bold green] Theme: {parts[1].strip()}")
                    print_banner()
                else:
                    console.print(f"Available themes: {', '.join(THEMES.keys())}")
                continue

            elif cmd in ["/summary", "summary"]:
                console.print(Panel(f"[bold {p}]Summary[/bold {p}]\n\nID: {current_session_id}\nCWD: {current_working_dir}\nMessages: {len(messages)}\nModel: {config.MODEL_NAME}", border_style=p))
                continue

            elif cmd == "/model":
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    new_model = parts[1].strip()
                    config.MODEL_NAME = new_model
                    console.print(f"[bold green]✔[/bold green] [white]Model switched to:[/white] [bold {p}]{new_model}[/bold {p}]")
                else:
                    console.print(f"[bold yellow]Current Model:[/bold yellow] {config.MODEL_NAME}")
                    console.print("[dim]Usage: /model <model_name>[/dim]")
                    console.print("[dim]Available models in config: " + ", ".join(config.AVAILABLE_MODELS["free"] + config.AVAILABLE_MODELS["paid"]) + "[/dim]")
                continue

            elif cmd == "/cd":
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    res = change_directory(parts[1].strip())
                    console.print(f"[bold {p}]>[/bold {p}] {res}")
                else:
                    console.print(f"[bold {p}]>[/bold {p}] Current directory: {current_working_dir}")
                continue

            elif cmd == "/conf":
                console.print(f"[bold {p}]╭─ Configuration Menu ───────────╮[/bold {p}]")
                console.print(f"[bold {p}]│[/bold {p}] [dim]Leave blank to keep current value[/dim]")
                new_url = console.input(f"[bold {p}]│[/bold {p}] [white]API URL [{config.MODEL_API_URL}]:[/white] ").strip()
                new_model = console.input(f"[bold {p}]│[/bold {p}] [white]Model [{config.MODEL_NAME}]:[/white] ").strip()
                new_key = console.input(f"[bold {p}]│[/bold {p}] [white]New API Key:[/white] ").strip()
                
                with open(config.GLOBAL_ENV_FILE, "a") as f:
                    if new_url:
                        config.MODEL_API_URL = new_url
                        f.write(f"\nMODEL_API_URL={new_url}\n")
                    if new_model:
                        config.MODEL_NAME = new_model
                        f.write(f"\nMODEL_NAME={new_model}\n")
                    if new_key:
                        config.MODEL_API_KEY = new_key
                        f.write(f"\nMODEL_API_KEY={new_key}\n")
                
                console.print(f"[bold {p}]╰──────────────────────────────╯[/bold {p}]")
                console.print(f"[bold green]✔ Configuration Updated![/bold green]")
                continue

            elif cmd == "/btw":
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    messages.append({"role": "user", "content": f"[BACKGROUND CONTEXT INJECTED]: {parts[1].strip()}"})
                    console.print(f"[bold green]✔[/bold green] Context appended silently. It will be sent with your next prompt.")
                else:
                    console.print("[dim]Usage: /btw <your background context>[/dim]")
                continue

            elif cmd == "/history":
                for i, m in enumerate(messages):
                    if m["role"] == "user":
                        console.print(f"[bold {p}]User:[/bold {p}] {str(m['content'])[:100]}...")
                    elif m["role"] == "assistant":
                        console.print(f"[bold {s}]Agent:[/bold {s}] {str(m.get('content', ''))[:100]}...")
                continue

            elif cmd == "/export":
                parts = user_input.split(" ", 1)
                fname = parts[1].strip() if len(parts) > 1 else f"export_{current_session_id}.md"
                with open(os.path.join(current_working_dir, fname), "w") as f:
                    for m in messages:
                        f.write(f"### {m['role'].upper()}\n{m.get('content', '')}\n\n")
                console.print(f"[bold green]✔[/bold green] Session exported to {os.path.join(current_working_dir, fname)}")
                continue

            elif cmd == "/rollback":
                if len(messages) > 1:
                    messages.pop() # remove last AI or tool
                    console.print(f"[bold yellow]↺ Rolled back last interaction.[/bold yellow]")
                else:
                    console.print("[red]Nothing to rollback.[/red]")
                continue

            elif cmd == "/system":
                console.print(Panel(os_info, title=f"[bold {p}]System Hardware[/bold {p}]", border_style=p))
                continue

            elif cmd == "/tokens":
                console.print(f"[bold {p}]Token Burn:[/bold {p}] {total_tokens_used:,} tokens used in this session.")
                continue

            if not user_input.strip() or user_input.startswith("/"):
                if user_input.startswith("/") and cmd not in ["/exit", "/clear", "/help", "/theme", "/summary", "/model", "/cd", "/conf", "/btw", "/history", "/export", "/rollback", "/system", "/tokens"]:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                continue
            
            # --- 3-AGENT AUTONOMOUS LOOP ---
            messages.append({"role": "user", "content": user_input})
            
            layout = generate_layout()
            p = current_theme["primary"]
            s = current_theme["secondary"]
            
            logo = f"[bold {p}]A E R I O N - X   D A S H B O A R D[/bold {p}]\n[white]BrahMos Cloud v6.0.0-PRO[/white]"
            layout["header"].update(Panel(Align.center(logo), style=p))
            layout["footer"].update(Panel(f"Status: Executing... | Tokens: {total_tokens_used}", style="dim"))
            
            chat_history_str = ""
            for m in messages[-6:]:
                role = "User" if m["role"] == "user" else "Agent"
                c = m.get('content') or '<Tool Call/Result>'
                chat_history_str += f"**{role}**: {c}\n\n"
            
            layout["chat"].update(Panel(Markdown(chat_history_str), title=f"[bold {p}]Terminal / History[/bold {p}]", border_style=p))
            
            layout["thinker"].update(Panel("Idle", title=f"[bold {p}]Thinker[/bold {p}]", border_style=p))
            layout["coder"].update(Panel("Idle", title=f"[bold {s}]Coder[/bold {s}]", border_style=s))
            layout["watchdog"].update(Panel("Idle", title=f"[bold red]Watchdog[/bold red]", border_style="red"))
            
            with Live(layout, refresh_per_second=15, screen=True) as live:
                # 1. Thinker Phase
                layout["thinker"].update(Panel("[bold yellow]Thinking...[/bold yellow]", title=f"[bold {p}]Thinker[/bold {p}]", border_style=p))
                thinker_messages = [{"role": "system", "content": THINKER_PROMPT}] + messages
                
                def thinker_stream(chunk, full):
                    layout["thinker"].update(Panel(Markdown(full), title=f"[bold {p}]Thinker[/bold {p}]", border_style=p))
                    layout["footer"].update(Panel(f"Status: Thinker Processing | Tokens: {total_tokens_used}", style="dim"))
                
                thinker_response = get_aerion_x_response(thinker_messages, use_tools=False, stream_callback=thinker_stream)
                plan_content = thinker_response.get("content", "")
                messages.append({"role": "assistant", "content": f"[Thinker Plan]:\n{plan_content}"})
                
                # 2. Coder Phase
                coder_messages = [{"role": "system", "content": CODER_PROMPT}] + messages
                coder_turns = 0
                max_coder_turns = 15
                fail_count = 0
                
                while coder_turns < max_coder_turns:
                    coder_turns += 1
                    layout["coder"].update(Panel("[bold yellow]Executing...[/bold yellow]", title=f"[bold {s}]Coder (Turn {coder_turns})[/bold {s}]", border_style=s))
                    
                    def coder_stream(chunk, full):
                        layout["coder"].update(Panel(Markdown(full), title=f"[bold {s}]Coder (Turn {coder_turns})[/bold {s}]", border_style=s))
                        layout["footer"].update(Panel(f"Status: Coder Generating | Tokens: {total_tokens_used}", style="dim"))
                        
                    response = get_aerion_x_response(coder_messages, use_tools=True, stream_callback=coder_stream)
                    coder_messages.append(response)
                    messages.append(response)
                    
                    if "tool_calls" in response and response["tool_calls"]:
                        for tc in response["tool_calls"]:
                            func = tc["function"]["name"]
                            try:
                                args = json.loads(tc["function"]["arguments"])
                            except:
                                args = {}
                                
                            layout["coder"].update(Panel(f"⚙️ Running Tool: [bold]{func}[/bold]...", title=f"[bold {s}]Coder Tool Execute[/bold {s}]", border_style=s))
                            total_tools_executed += 1
                            
                            try:
                                res = TOOLS[func](**args)
                            except Exception as e:
                                res = f"Tool execution failed: {str(e)}"
                                
                            tool_msg = {"role": "tool", "tool_call_id": tc["id"], "name": func, "content": str(res)}
                            coder_messages.append(tool_msg)
                            messages.append(tool_msg)
                            
                            if func == "run_shell" and ("Error" in str(res) or "Exception" in str(res) or "failed" in str(res).lower()):
                                fail_count += 1
                                
                        if fail_count >= 5:
                            break
                        continue
                    break # Coder done
                
                # 3. Watchdog Phase
                if fail_count >= 5:
                    layout["watchdog"].update(Panel("[bold yellow]Debugging...[/bold yellow]", title="[bold red]Watchdog[/bold red]", border_style="red"))
                    debugger_messages = [{"role": "system", "content": DEBUGGER_PROMPT}] + messages
                    
                    debugger_turns = 0
                    while debugger_turns < 10:
                        debugger_turns += 1
                        
                        def watchdog_stream(chunk, full):
                            layout["watchdog"].update(Panel(Markdown(full), title=f"[bold red]Watchdog (Turn {debugger_turns})[/bold red]", border_style="red"))
                            layout["footer"].update(Panel(f"Status: Watchdog Analyzing | Tokens: {total_tokens_used}", style="dim"))
                            
                        response = get_aerion_x_response(debugger_messages, use_tools=True, stream_callback=watchdog_stream)
                        debugger_messages.append(response)
                        messages.append(response)
                        
                        if "tool_calls" in response and response["tool_calls"]:
                            for tc in response["tool_calls"]:
                                func = tc["function"]["name"]
                                try:
                                    args = json.loads(tc["function"]["arguments"])
                                except:
                                    args = {}
                                    
                                layout["watchdog"].update(Panel(f"⚙️ Running Tool: [bold]{func}[/bold]...", title="[bold red]Watchdog Tool Execute[/bold red]", border_style="red"))
                                total_tools_executed += 1
                                
                                try:
                                    res = TOOLS[func](**args)
                                except Exception as e:
                                    res = f"Tool execution failed: {str(e)}"
                                    
                                tool_msg = {"role": "tool", "tool_call_id": tc["id"], "name": func, "content": str(res)}
                                debugger_messages.append(tool_msg)
                                messages.append(tool_msg)
                            continue
                        break # Debugger done
            
            final_content = ""
            for m in reversed(messages):
                if m["role"] == "assistant" and "tool_calls" not in m:
                    final_content = m.get("content", "")
                    break
            
            if final_content:
                console.print(Panel(Markdown(final_content), title=f"[bold {p}]Agent Response[/bold {p}]", border_style=p))
                
            save_session(current_session_id, messages)
        except KeyboardInterrupt: 
            console.print("\n[bold red]Operation cancelled.[/bold red]")
            break
        except Exception as e: 
            log_error(str(e))

if __name__ == "__main__": main()
