# functions/get_file_content.py
import os
from .config import MAX_FILE_CHARS
from google.genai import types



def get_file_content(working_directory, file_path):
    """
    Safely read and return the contents of a file located under working_directory.

    - working_directory: base directory that bounds allowed file access.
    - file_path: path relative to working_directory (may include subfolders).
    Returns:
      - file contents as a string, possibly truncated, OR
      - an error string prefixed with "Error:" on failure.
    """
    try:
        # Ensure working_directory is an absolute path
        working_abs = os.path.abspath(working_directory)

        # Build the absolute path to the requested file (treat file_path as relative)
        full_path = os.path.abspath(os.path.join(working_abs, file_path))

        # Security check: ensure full_path is inside working_directory
        # Use commonpath to avoid false positives (e.g., /home/user/dir and /home/user/dir2)
        if os.path.commonpath([working_abs, full_path]) != working_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Ensure the path is a regular file
        if not os.path.isfile(full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # Read the file safely (replace malformed characters if any)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Truncate if longer than allowed length, append a clear message
        if len(content) > MAX_FILE_CHARS:
            truncated = content[:MAX_FILE_CHARS]
            truncated += f'\n[...File "{file_path}" truncated at {MAX_FILE_CHARS} characters]'
            return truncated

        return content

    except Exception as e:
        # Always return error strings prefixed with "Error:"
        return f"Error: {str(e)}"

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the text contents of a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to read."
            )
        },
        required=["file_path"]
    )
)
