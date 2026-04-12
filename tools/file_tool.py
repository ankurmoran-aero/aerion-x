import os

def list_files(path="Workspace"):
    """Lists files in the specified directory."""
    try:
        files = os.listdir(path)
        if not files:
            return "Directory is empty."
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file(file_path):
    """Reads content from a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path, content):
    """Writes content to a file, automatically creating parent directories."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def replace_text(file_path, old_string, new_string, allow_multiple=False):
    """Replaces occurrences of old_string with new_string in a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        count = content.count(old_string)
        if count == 0:
            return f"Error: old_string not found in {file_path}"
        if count > 1 and not allow_multiple:
            return f"Error: old_string found {count} times in {file_path}, but allow_multiple is False."
            
        new_content = content.replace(old_string, new_string)
        with open(file_path, 'w') as f:
            f.write(new_content)
        return f"Successfully replaced {count} occurrences in {file_path}"
    except Exception as e:
        return f"Error replacing text in file: {str(e)}"

def search_directory(query, path="Workspace"):
    """Searches for files by name or content within a directory."""
    try:
        results = []
        for root, _, files in os.walk(path):
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if query.lower() in f.read().lower():
                            results.append(file_path)
                except UnicodeDecodeError:
                    pass # Skip binary files
        if not results:
            return "No matches found."
        return "\n".join(results[:50]) # limit output
    except Exception as e:
        return f"Error searching directory: {str(e)}"

