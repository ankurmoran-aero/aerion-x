import re

with open("setup.py", "r") as f:
    setup_content = f.read()
setup_content = setup_content.replace('version="6.2.0"', 'version="6.3.0"')
with open("setup.py", "w") as f:
    f.write(setup_content)

with open("main.py", "r") as f:
    main_content = f.read()
main_content = main_content.replace('v6.2.0-PRO', 'v6.3.0-PRO')
with open("main.py", "w") as f:
    f.write(main_content)
