# functions/write_file.py
import os
from google.genai import types

def write_file(working_directory, file_path, content):
    """
    Safely write content to a file located under working_directory.

    - working_directory: base directory that bounds allowed file writes.
    - file_path: path relative to working_directory (may include subfolders).
    - content: string to write to the file.

    Returns:
      - Success string if write was successful
      - Error string prefixed with "Error:" on failure
    """
    try:
        # Absolute paths
        working_abs = os.path.abspath(working_directory)
        full_path = os.path.abspath(os.path.join(working_abs, file_path))

        # Security check
        if os.path.commonpath([working_abs, full_path]) != working_abs:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Create directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {str(e)}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite content to a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Where to write the file."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The text to write."
            )
        },
        required=["file_path", "content"]
    )
)
