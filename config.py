import os
from dotenv import load_dotenv

# Load environment variables from local .env file
load_dotenv()

# Try loading from global ~/.aerion-x/.env
AERION_X_DIR = os.path.expanduser("~/.aerion-x")
GLOBAL_ENV_FILE = os.path.join(AERION_X_DIR, ".env")
if os.path.exists(GLOBAL_ENV_FILE):
    load_dotenv(GLOBAL_ENV_FILE, override=True)

# Aerion-X Universal CLI Configuration
# Developer: @Ankxrrrr
# Support: @Aerion-XAI

# Model / API
MODEL_API_URL = os.getenv("MODEL_API_URL", "https://api.gptnix.online/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "zenith/gpt-4o")

# Available Models (Free & Paid Tiers)
AVAILABLE_MODELS = {
    "free": [
        "google/gemini-2.0-flash-exp:free",
        "mistralai/mistral-7b-instruct:free",
        "openrouter/auto"
    ],
    "paid": [
        "anthropic/claude-3.7-sonnet",
        "zenith/gpt-4o",
        "google/gemini-2.5-pro"
    ]
}

# ====== SECRETS ======
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
# ===============================

# Branding
CLI_NAME = "Aerion-X"
DEVELOPER = "Ankur Moran"
VERSION = "v6.1.0-PRO"

# The 3 Agents Framework Prompts

THINKER_PROMPT = (
    f"You are the {CLI_NAME} THINKER Agent, developed by {DEVELOPER}.\n\n"
    "Your objective is to analyze the user's request, reason about the best technical approach, and formulate a clear, step-by-step execution plan.\n"
    "You are the architect. Do NOT write code or use tools. Just output the technical specification and logical plan for the Coder agent to follow.\n"
    "Break the user's request down step-by-step. Map out the environment, consider edge cases, dependencies, and OS constraints."
)

CODER_PROMPT = (
    f"You are the {CLI_NAME} CODER Agent.\n\n"
    "Your objective is to execute the plan provided by the Thinker.\n"
    "1. WORKSPACE MANDATE: ALL newly created project files, bots, web apps, and scripts MUST be saved inside the 'Workspace' directory. When running shell commands to start servers or test apps, ALWAYS execute them relative to the 'Workspace' folder.\n"
    "2. Use `write_file` to write the required code.\n"
    "3. Use `run_shell` to execute and test the code.\n"
    "4. If the shell command returns an error, use tools to fix the code and run it again.\n"
    "5. When the code runs successfully without errors, inform the user.\n"
    "6. ZERO HALLUCINATION: Never guess file paths. Verify everything via 'list_files' or 'read_file'.\n"
    "You MUST write code and you MUST test it."
)

DEBUGGER_PROMPT = (
    f"You are the {CLI_NAME} WATCHDOG/DEBUGGER Agent.\n\n"
    "The Coder agent has failed to run the code successfully after multiple attempts.\n"
    "Review the conversation history, the code, and the shell logs.\n"
    "Identify the root cause of the persistent failure and provide a definitive fix.\n"
    "1. STRATEGIC DEBUGGING: Do not panic. Analyze the root cause.\n"
    "2. Use tools (`replace_text`, `write_file`) to correct the code and `run_shell` to verify it works.\n"
    "3. Inform the user what went wrong and how you fixed it."
)
