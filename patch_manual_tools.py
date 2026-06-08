import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Update payload construction
old_payload_logic = """    payload = {"model": config.MODEL_NAME, "messages": messages, "temperature": 0.2}
    
    if use_tools:
        tools_config = ["""

new_payload_logic = """    payload = {"model": config.MODEL_NAME, "messages": list(messages), "temperature": 0.2}
    
    supports_native_tools = True
    if "claude" in config.MODEL_NAME.lower() or "grok" in config.MODEL_NAME.lower():
        supports_native_tools = False

    if use_tools and supports_native_tools:
        tools_config = ["""

content = content.replace(old_payload_logic, new_payload_logic)

old_tools_assign = """        payload["tools"] = tools_config
        payload["tool_choice"] = "auto"
    
    if stream_callback:"""

new_tools_assign = """        payload["tools"] = tools_config
        payload["tool_choice"] = "auto"
    elif use_tools and not supports_native_tools:
        manual_prompt = "You do not support native tool calling. To execute a tool, output a JSON block formatted EXACTLY like this:\\n```json\\n{\\n  \\"tool_calls\\": [\\n    {\\n      \\"name\\": \\"run_shell\\",\\n      \\"arguments\\": {\\"command\\": \\"ls -la\\"}\\n    }\\n  ]\\n}\\n```\\nDo not output anything else if you want to call a tool."
        payload["messages"].append({"role": "system", "content": manual_prompt})
    
    if stream_callback:"""

content = content.replace(old_tools_assign, new_tools_assign)

# 2. Update response parsing for both stream and non-stream
old_return_stream = """            if tool_calls:
                final_message["tool_calls"] = list(tool_calls.values())
            
            total_tokens_used += int(len(full_content) / 4) # Approximation
            return final_message"""

new_return_stream = """            if tool_calls:
                final_message["tool_calls"] = list(tool_calls.values())
            
            total_tokens_used += int(len(full_content) / 4) # Approximation
            
            if use_tools and not supports_native_tools:
                import re
                c = final_message.get("content", "")
                if "```json" in c:
                    match = re.search(r'```json\\s*(\\{.*?\\})\\s*```', c, re.DOTALL)
                    if match:
                        try:
                            import json
                            parsed = json.loads(match.group(1))
                            if "tool_calls" in parsed:
                                final_message["tool_calls"] = []
                                for idx, tc in enumerate(parsed["tool_calls"]):
                                    final_message["tool_calls"].append({
                                        "id": f"call_{idx}",
                                        "type": "function",
                                        "function": {
                                            "name": tc.get("name", ""),
                                            "arguments": json.dumps(tc.get("arguments", {}))
                                        }
                                    })
                                final_message["content"] = c.replace(match.group(0), "").strip()
                        except:
                            pass
            return final_message"""

content = content.replace(old_return_stream, new_return_stream)

old_return_nonstream = """            data = resp.json()
            if "usage" in data:
                total_tokens_used += data["usage"].get("total_tokens", 0)
            return data["choices"][0]["message"]"""

new_return_nonstream = """            data = resp.json()
            if "usage" in data:
                total_tokens_used += data["usage"].get("total_tokens", 0)
            final_message = data["choices"][0]["message"]
            
            if use_tools and not supports_native_tools:
                import re
                c = final_message.get("content", "")
                if c and "```json" in c:
                    match = re.search(r'```json\\s*(\\{.*?\\})\\s*```', c, re.DOTALL)
                    if match:
                        try:
                            import json
                            parsed = json.loads(match.group(1))
                            if "tool_calls" in parsed:
                                final_message["tool_calls"] = []
                                for idx, tc in enumerate(parsed["tool_calls"]):
                                    final_message["tool_calls"].append({
                                        "id": f"call_{idx}",
                                        "type": "function",
                                        "function": {
                                            "name": tc.get("name", ""),
                                            "arguments": json.dumps(tc.get("arguments", {}))
                                        }
                                    })
                                final_message["content"] = c.replace(match.group(0), "").strip()
                        except:
                            pass
            return final_message"""

content = content.replace(old_return_nonstream, new_return_nonstream)

with open("main.py", "w") as f:
    f.write(content)
