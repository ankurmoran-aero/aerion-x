import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Add prompt_toolkit to dependencies
content = content.replace(
    'required = ["colorama", "requests", "beautifulsoup4", "googlesearch-python", "rich", "python-dotenv"]',
    'required = ["colorama", "requests", "beautifulsoup4", "googlesearch-python", "rich", "python-dotenv", "prompt_toolkit"]'
)

# 2. Update imports
import_block = """from rich.align import Align
console = Console()

# --- Autocomplete ---
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as PTStyle
"""
content = content.replace("from rich.align import Align\nconsole = Console()", import_block)

# 3. Update main() startup onboarding
onboarding_old = """    if not config.MODEL_API_KEY:
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
            f.write(f"\\nMODEL_API_KEY={api_key}\\n")
            
        config.MODEL_API_KEY = api_key
        console.print("[bold green]API Key saved successfully! You can update it later in ~/.aerion-x/.env[/bold green]\\n")"""

onboarding_new = """    if not config.MODEL_API_KEY:
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
                    f.write(f"\\nMODEL_API_KEY={api_key}\\n")
                config.MODEL_API_KEY = api_key
                console.print("[bold green]✔ Official API Key saved![/bold green]\\n")
            else:
                console.print("[bold red]Error: API Key is required.[/bold red]")
                sys.exit(1)
        else:
            console.print("\\n[bold yellow]Custom API Setup[/bold yellow]")
            try:
                api_url = console.input("[white]Enter API URL Endpoint (e.g., https://api.openai.com/v1/chat/completions): [/white]").strip()
                api_model = console.input("[white]Enter Model Name (e.g., gpt-4o): [/white]").strip()
                api_key = console.input("[white]Enter API Key: [/white]").strip()
            except EOFError:
                api_url = api_model = api_key = ""
                
            if api_url and api_model and api_key:
                with open(config.GLOBAL_ENV_FILE, "a") as f:
                    f.write(f"\\nMODEL_API_URL={api_url}\\nMODEL_NAME={api_model}\\nMODEL_API_KEY={api_key}\\n")
                config.MODEL_API_URL = api_url
                config.MODEL_NAME = api_model
                config.MODEL_API_KEY = api_key
                console.print("[bold green]✔ Custom API Setup saved![/bold green]\\n")
            else:
                console.print("[bold red]Error: All fields are required for custom setup.[/bold red]")
                sys.exit(1)"""

content = content.replace(onboarding_old, onboarding_new)

# 4. Update the input prompt
input_old = """            try:
                user_input = console.input(f"\\n[bold {p}]╭─ You[/bold {p}] [dim]({cwd_name})[/dim]\\n[bold {p}]╰─❯ [/bold {p}]")
            except EOFError:
                user_input = "/exit\""""

input_new = """            try:
                console.print(f"\\n[bold {p}]╭─ You[/bold {p}] [dim]({cwd_name})[/dim]")
                slash_commands = ['/help', '/conf', '/theme', '/model', '/cd', '/btw', '/history', '/export', '/rollback', '/summary', '/system', '/tokens', '/exit', '/clear']
                cmd_completer = WordCompleter(slash_commands, ignore_case=True, match_middle=False)
                
                # We use prompt_toolkit so autocomplete drops down menus when typing /
                user_input = prompt("╰─❯ ", completer=cmd_completer)
            except EOFError:
                user_input = "/exit\""""

content = content.replace(input_old, input_new)

# 5. Update /conf command
conf_old = """            elif cmd == "/conf":
                console.print(f"[bold {p}]╭─ Configuration Menu ───────────╮[/bold {p}]")
                new_key = console.input(f"[bold {p}]│[/bold {p}] [white]New API Key (leave blank to skip):[/white] ").strip()
                if new_key:
                    config.MODEL_API_KEY = new_key
                    with open(config.GLOBAL_ENV_FILE, "a") as f: f.write(f"\\nMODEL_API_KEY={new_key}\\n")
                    console.print(f"[bold {p}]│[/bold {p}] [bold green]✔ API Key Updated![/bold green]")
                console.print(f"[bold {p}]╰──────────────────────────────╯[/bold {p}]")
                continue"""

conf_new = """            elif cmd == "/conf":
                console.print(f"[bold {p}]╭─ Configuration Menu ───────────╮[/bold {p}]")
                console.print(f"[bold {p}]│[/bold {p}] [dim]Leave blank to keep current value[/dim]")
                new_url = console.input(f"[bold {p}]│[/bold {p}] [white]API URL [{config.MODEL_API_URL}]:[/white] ").strip()
                new_model = console.input(f"[bold {p}]│[/bold {p}] [white]Model [{config.MODEL_NAME}]:[/white] ").strip()
                new_key = console.input(f"[bold {p}]│[/bold {p}] [white]New API Key:[/white] ").strip()
                
                with open(config.GLOBAL_ENV_FILE, "a") as f:
                    if new_url:
                        config.MODEL_API_URL = new_url
                        f.write(f"\\nMODEL_API_URL={new_url}\\n")
                    if new_model:
                        config.MODEL_NAME = new_model
                        f.write(f"\\nMODEL_NAME={new_model}\\n")
                    if new_key:
                        config.MODEL_API_KEY = new_key
                        f.write(f"\\nMODEL_API_KEY={new_key}\\n")
                
                console.print(f"[bold {p}]╰──────────────────────────────╯[/bold {p}]")
                console.print(f"[bold green]✔ Configuration Updated![/bold green]")
                continue"""

content = content.replace(conf_old, conf_new)

with open("main.py", "w") as f:
    f.write(content)
