with open("main.py", "r") as f:
    content = f.read()

content = content.replace("BrahMos Cloud", "Aerion-X Net")
content = content.replace("Terminate connection to Aerion-X Net", "Terminate connection to Aerion-X")

with open("main.py", "w") as f:
    f.write(content)
