🚀 AI Coding Agent — Boot.dev Project

An AI-powered coding agent that can:

List files and directories

Read file contents

Write and overwrite files

Execute Python files (with arguments)

Use these tools autonomously inside a 20-step feedback loop

Fix bugs in the calculator application without human intervention

This project implements a real agent system using Google Gemini, tool/function calling, and a message-based iterative loop.

AI_Agent/
│
├── main.py                        # The agent system / message loop
├── functions/
│   ├── get_files_info.py          # Safe directory listing
│   ├── get_file_content.py        # Controlled file read
│   ├── write_file.py              # Controlled file write
│   ├── run_python_file.py         # Safe Python execution w/ subprocess
│
├── calculator/
│   ├── main.py                    # CLI calculator program
│   └── pkg/
│       ├── calculator.py          # Expression parser (bug fixed by agent)
│       └── render.py              # Output formatting
│
├── tests.py                       # Boot.dev tests
└── README.md

⚙️ How It Works
1. Function Declarations (Schemas)

Each tool includes a schema_… object describing:

function name

description

expected parameters

argument shapes

These are given to Gemini so it knows how to call your tools.

2. Function Execution Layer

call_function():

Receives types.FunctionCall

Injects a secure working_directory = "calculator"

Maps function names → actual Python functions

Executes the function

Wraps the return value in:

types.Part.from_function_response(...)


This allows Gemini to use the result as the next message in the conversation.

3. Agent Feedback Loop

Your main.py:

Maintains a structured messages list

Calls Gemini repeatedly (max 20 iterations)

Detects tool calls

Executes tools

Appends tool results back into the conversation

Continues until Gemini returns a non-function-calling natural language answer

This loop is what transforms the model into an agent.

🧪 Running the Calculator
uv run calculator/main.py "3 + 7 * 2"

🤖 Running the Agent
Basic usage:
uv run main.py "list the files inside pkg"

Fixing a real bug:
uv run main.py "fix the bug: 3 + 7 * 2 shouldn't be 20"

Verbose mode:
uv run main.py "read calculator.py" --verbose

🛠 Commands the Agent Can Use
✔ List files
get_files_info(directory="pkg")

✔ Read file contents
get_file_content(file_path="main.py")

✔ Write or overwrite files
write_file(file_path="lorem.txt", content="hi")

✔ Execute Python files
run_python_file(file_path="main.py", args=["3 + 5"])


All paths are relative and securely sandboxed under:

calculator/


📚 Requirements

Python 3.11+

uv package runner

Google Gemini API key

Add it to .env:

GEMINI_API_KEY=your_key_here

🚀 Run Tests (Boot.dev)
uv run tests.py