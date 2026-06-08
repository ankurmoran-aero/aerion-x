import re

with open("main.py", "r") as f:
    content = f.read()

# Remove generate_layout()
content = re.sub(r'def generate_layout\(\):.*?return layout\n', '', content, flags=re.DOTALL)

# Replace the 3-AGENT AUTONOMOUS LOOP UI with a rich Status spinner
old_loop_start = """            # --- 3-AGENT AUTONOMOUS LOOP ---
            messages.append({"role": "user", "content": user_input})
            
            layout = generate_layout()
            p = current_theme["primary"]
            s = current_theme["secondary"]"""

new_loop_start = """            # --- 3-AGENT AUTONOMOUS LOOP ---
            messages.append({"role": "user", "content": user_input})
            p = current_theme["primary"]
            s = current_theme["secondary"]
            
            from rich.status import Status"""

content = content.replace(old_loop_start, new_loop_start)

# Replace the layout logic
old_ui_logic = """            logo = f"[bold {p}]A E R I O N - X   D A S H B O A R D[/bold {p}]\\n[white]Aerion-X Net v6.0.0-PRO[/white]"
            layout["header"].update(Panel(Align.center(logo), style=p))
            layout["footer"].update(Panel(f"Status: Executing... | Tokens: {total_tokens_used}", style="dim"))
            
            chat_history_str = ""
            for m in messages[-6:]:
                role = "User" if m["role"] == "user" else "Agent"
                c = m.get('content') or '<Tool Call/Result>'
                chat_history_str += f"**{role}**: {c}\\n\\n"
            
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
                messages.append({"role": "assistant", "content": f"[Thinker Plan]:\\n{plan_content}"})
                
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
                        break # Debugger done"""

new_ui_logic = """            with Status(f"[bold {p}]Agent is reasoning...[/bold {p}]", spinner="dots") as status:
                # 1. Thinker Phase
                thinker_messages = [{"role": "system", "content": THINKER_PROMPT}] + messages
                thinker_response = get_aerion_x_response(thinker_messages, use_tools=False, stream_callback=None)
                plan_content = thinker_response.get("content", "")
                messages.append({"role": "assistant", "content": f"[Thinker Plan]:\\n{plan_content}"})
                
                # 2. Coder Phase
                status.update(f"[bold {s}]Executing tasks...[/bold {s}]")
                coder_messages = [{"role": "system", "content": CODER_PROMPT}] + messages
                coder_turns = 0
                max_coder_turns = 15
                fail_count = 0
                
                while coder_turns < max_coder_turns:
                    coder_turns += 1
                    status.update(f"[bold {s}]Generating code/tools...[/bold {s}]")
                    response = get_aerion_x_response(coder_messages, use_tools=True, stream_callback=None)
                    coder_messages.append(response)
                    messages.append(response)
                    
                    if "tool_calls" in response and response["tool_calls"]:
                        for tc in response["tool_calls"]:
                            func = tc["function"]["name"]
                            try:
                                args = json.loads(tc["function"]["arguments"])
                            except:
                                args = {}
                                
                            status.update(f"[bold cyan]⚙️ Running tool:[/bold cyan] {func}...")
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
                    status.update(f"[bold red]Watchdog debugging error loop...[/bold red]")
                    debugger_messages = [{"role": "system", "content": DEBUGGER_PROMPT}] + messages
                    debugger_turns = 0
                    
                    while debugger_turns < 10:
                        debugger_turns += 1
                        status.update(f"[bold red]Debugging...[/bold red]")
                        response = get_aerion_x_response(debugger_messages, use_tools=True, stream_callback=None)
                        debugger_messages.append(response)
                        messages.append(response)
                        
                        if "tool_calls" in response and response["tool_calls"]:
                            for tc in response["tool_calls"]:
                                func = tc["function"]["name"]
                                try:
                                    args = json.loads(tc["function"]["arguments"])
                                except:
                                    args = {}
                                    
                                status.update(f"[bold cyan]⚙️ Debugging Tool:[/bold cyan] {func}...")
                                total_tools_executed += 1
                                
                                try:
                                    res = TOOLS[func](**args)
                                except Exception as e:
                                    res = f"Tool execution failed: {str(e)}"
                                    
                                tool_msg = {"role": "tool", "tool_call_id": tc["id"], "name": func, "content": str(res)}
                                debugger_messages.append(tool_msg)
                                messages.append(tool_msg)
                            continue
                        break # Debugger done"""

content = content.replace(old_ui_logic, new_ui_logic)

with open("main.py", "w") as f:
    f.write(content)
