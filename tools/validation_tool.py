import subprocess
import os

def validate_code(file_path):
    """Validates the syntax of a Python or JavaScript/TypeScript file."""
    if not os.path.exists(file_path):
        return f"Error: File {file_path} does not exist."
    
    ext = os.path.splitext(file_path)[1]
    
    try:
        if ext == ".py":
            result = subprocess.run(["python3", "-m", "py_compile", file_path], capture_output=True, text=True)
            if result.returncode == 0:
                return "Syntax Check: OK (Python)"
            else:
                return f"Syntax Check: FAILED\n{result.stderr}"
        
        elif ext in [".js", ".ts"]:
            # Check if node exists
            if not subprocess.run(["which", "node"], capture_output=True).returncode == 0:
                return "Syntax Check: Skipped (Node.js not installed)"
            
            # Simple node syntax check
            result = subprocess.run(["node", "--check", file_path], capture_output=True, text=True)
            if result.returncode == 0:
                return "Syntax Check: OK (JavaScript)"
            else:
                return f"Syntax Check: FAILED\n{result.stderr}"
        
        else:
            return f"Syntax Check: Unsupported file type ({ext})"
            
    except Exception as e:
        return f"Error during validation: {str(e)}"
