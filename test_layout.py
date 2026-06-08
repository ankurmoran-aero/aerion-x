import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.align import Align

console = Console()

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

layout = generate_layout()
layout["header"].update(Panel(Align.center("[bold cyan]A E R I O N - X   D A S H B O A R D[/bold cyan]\n[white]BrahMos Cloud v6.0.0[/white]"), style="cyan"))
layout["chat"].update(Panel("Chat History...", title="[bold cyan]Terminal[/bold cyan]", border_style="cyan"))
layout["thinker"].update(Panel("Idle", title="[bold purple]Thinker[/bold purple]", border_style="purple"))
layout["coder"].update(Panel("Idle", title="[bold blue]Coder[/bold blue]", border_style="blue"))
layout["watchdog"].update(Panel("Idle", title="[bold red]Watchdog[/bold red]", border_style="red"))
layout["footer"].update(Panel("Status: Ready | Tokens: 0", style="dim"))

with Live(layout, refresh_per_second=10, screen=True) as live:
    for i in range(30):
        layout["thinker"].update(Panel(f"Thinking... {i}", title="[bold purple]Thinker[/bold purple]", border_style="purple"))
        time.sleep(0.1)
