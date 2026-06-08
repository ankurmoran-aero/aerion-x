import requests
import os

url = "https://api.gptnix.online/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-av-v1-noq_Ig2pG6epdhC880sybnd4Sb_j2zs4ZiZUj5tDK05HqhLgy7GcwwGrnyloFufcEuf7_8jMcQRP2RsWIwXBk4Gwmdw2IU5jvKPWRQ58cO7sUlZSsfWBKAj",
    "Content-Type": "application/json"
}
data = {
    "model": "zenith/gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
}
response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)
