import json
import sys
import os
import subprocess
import platform
import shutil
from datetime import datetime

# --- Auto-Install Dependencies ---
def ensure_dependencies():
    required = ["colorama", "requests", "beautifulsoup4", "googlesearch-python", "rich", "python-dotenv"]
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
console = Console()

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
    
    panel = Panel(
        Align.center(logo) + "\n" + table,
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
def get_aerion_x_response(messages, use_tools=True):
    global total_tokens_used
    messages = trim_messages(messages)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MODEL_API_KEY}",
        "HTTP-Referer": "https://github.com/ankurmoran-aero/aerion-x",
        "X-Title": "Aerion-X"
    }

    payload = {"model": MODEL_NAME, "messages": messages, "temperature": 0.2}
    
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
    
    try:
        resp = requests.post(MODEL_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Track Token Usage
        if "usage" in data:
            total_tokens_used += data["usage"].get("total_tokens", 0)
            
        return data["choices"][0]["message"]
    except Exception as e:
        return {"role": "assistant", "content": f"Aerion-X API Error: {str(e)}"}

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
        console.print("[white]To get started, please provide your API Key (e.g., from OpenRouter, OpenAI, or GPTNix).[/white]")
        try:
            api_key = input("API Key: ").strip()
        except EOFError:
            api_key = ""
            
        if not api_key:
            console.print("[bold red]Error: API Key is required to run Aerion-X.[/bold red]")
            sys.exit(1)
        
        os.makedirs(config.AERION_X_DIR, exist_ok=True)
        with open(config.GLOBAL_ENV_FILE, "a") as f:
            f.write(f"\nMODEL_API_KEY={api_key}\n")
            
        config.MODEL_API_KEY = api_key
        console.print("[bold green]API Key saved successfully! You can update it later in ~/.aerion-x/.env[/bold green]\n")
    
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
                user_input = console.input(f"\n[bold {p}]╭─ You[/bold {p}] [dim]({cwd_name})[/dim]\n[bold {p}]╰─❯ [/bold {p}]")
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
                from rich.panel import Panel
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
                new_key = console.input(f"[bold {p}]│[/bold {p}] [white]New API Key (leave blank to skip):[/white] ").strip()
                if new_key:
                    config.MODEL_API_KEY = new_key
                    with open(config.GLOBAL_ENV_FILE, "a") as f: f.write(f"\nMODEL_API_KEY={new_key}\n")
                    console.print(f"[bold {p}]│[/bold {p}] [bold green]✔ API Key Updated![/bold green]")
                console.print(f"[bold {p}]╰──────────────────────────────╯[/bold {p}]")
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
            
            # 1. Thinker Phase
            with console.status(f"[bold {p}]Thinker Agent is mapping neural pathways...[/bold {p}]", spinner="bouncingBar", spinner_style=p) as status:
                thinker_messages = [{"role": "system", "content": THINKER_PROMPT}] + messages
                thinker_response = get_aerion_x_response(thinker_messages, use_tools=False)
                plan_content = thinker_response.get("content", "")
                
                status.stop()
                log_aerion_x(plan_content, title="Thinker Agent")
                status.start()
                
                messages.append({"role": "assistant", "content": f"[Thinker Plan]:\n{plan_content}"})
            
            # 2. Coder Phase
            with console.status(f"[bold {p}]Coder Agent is executing directives...[/bold {p}]", spinner="aesthetic", spinner_style=p) as status:
                coder_messages = [{"role": "system", "content": CODER_PROMPT}] + messages
                
                coder_turns = 0
                max_coder_turns = 15
                fail_count = 0
                
                while coder_turns < max_coder_turns:
                    coder_turns += 1
                    response = get_aerion_x_response(coder_messages, use_tools=True)
                    coder_messages.append(response)
                    messages.append(response)
                    
                    if response.get("content"):
                        status.stop()
                        log_aerion_x(response["content"], title="Coder Agent")
                        status.start()
                        
                    if "tool_calls" in response and response["tool_calls"]:
                        for tc in response["tool_calls"]:
                            func = tc["function"]["name"]
                            try:
                                args = json.loads(tc["function"]["arguments"])
                            except:
                                args = {}
                                
                            status.stop(); log_tool(f"Coder running {func}..."); 
                            
                            # Track tool execution
                            total_tools_executed += 1
                            
                            # Execute Tool
                            try:
                                res = TOOLS[func](**args)
                            except Exception as e:
                                res = f"Tool execution failed: {str(e)}"
                                
                            tool_msg = {"role": "tool", "tool_call_id": tc["id"], "name": func, "content": str(res)}
                            coder_messages.append(tool_msg)
                            messages.append(tool_msg)
                            status.start()
                            
                            # Check if the shell command failed
                            if func == "run_shell" and ("Error" in str(res) or "Exception" in str(res) or "failed" in str(res).lower()):
                                fail_count += 1
                                status.stop()
                                log_error(f"Execution failed! (Attempt {fail_count}/5)")
                                status.start()
                                
                        if fail_count >= 5:
                            status.stop()
                            log_error("Coder Agent failed 5 times! Waking up Watchdog Agent...")
                            status.start()
                            break # Break coder loop, trigger debugger
                        continue
                    break # Coder finished successfully
            
            # 3. Watchdog Phase
            if fail_count >= 5:
                with console.status(f"[bold {p}]Watchdog Agent is reverse-engineering failures...[/bold {p}]", spinner="grenade", spinner_style=p) as status:
                    debugger_messages = [{"role": "system", "content": DEBUGGER_PROMPT}] + messages
                    
                    debugger_turns = 0
                    while debugger_turns < 10:
                        debugger_turns += 1
                        response = get_aerion_x_response(debugger_messages, use_tools=True)
                        debugger_messages.append(response)
                        messages.append(response)
                        
                        if response.get("content"):
                            status.stop()
                            log_aerion_x(response["content"], title="Watchdog Agent")
                            status.start()
                            
                        if "tool_calls" in response and response["tool_calls"]:
                            for tc in response["tool_calls"]:
                                func = tc["function"]["name"]
                                try:
                                    args = json.loads(tc["function"]["arguments"])
                                except:
                                    args = {}
                                    
                                status.stop(); log_tool(f"Watchdog running {func}..."); 
                                
                                # Track tool execution
                                total_tools_executed += 1
                                
                                try:
                                    res = TOOLS[func](**args)
                                except Exception as e:
                                    res = f"Tool execution failed: {str(e)}"
                                    
                                tool_msg = {"role": "tool", "tool_call_id": tc["id"], "name": func, "content": str(res)}
                                debugger_messages.append(tool_msg)
                                messages.append(tool_msg)
                                status.start()
                            continue
                        break # Debugger finished
            
            save_session(current_session_id, messages)
        except KeyboardInterrupt: 
            console.print("\n[bold red]Operation cancelled.[/bold red]")
            break
        except Exception as e: 
            log_error(str(e))

if __name__ == "__main__": main()
