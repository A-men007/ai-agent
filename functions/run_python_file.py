# functions/run_python_file.py
import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    """
    Safely execute a Python file within the working directory.

    - working_directory: base directory that bounds allowed execution.
    - file_path: relative path to the Python file.
    - args: list of command-line arguments to pass.

    Returns:
      - A formatted string with STDOUT, STDERR, and exit code info.
      - Error string if execution is disallowed or fails.
    """
    try:
        # Build safe absolute paths
        working_abs = os.path.abspath(working_directory)
        full_path = os.path.abspath(os.path.join(working_abs, file_path))

        # Security check
        if os.path.commonpath([working_abs, full_path]) != working_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Check file existence
        if not os.path.exists(full_path):
            return f'Error: File "{file_path}" not found.'

        # Check that it's a Python file
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # Run the file safely
        result = subprocess.run(
            ["python3", full_path] + args,
            cwd=working_abs,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Collect output
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if not stdout and not stderr:
            return "No output produced."

        output_parts = []
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")

        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file with optional command-line args.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python file to run."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Arguments to pass.",
                items=types.Schema(type=types.Type.STRING)
            )
        },
        required=["file_path"]
    )
)
