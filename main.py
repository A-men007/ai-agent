import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import functions + schemas
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.write_file import write_file, schema_write_file
from functions.run_python_file import run_python_file, schema_run_python_file

system_prompt = """
You are a helpful AI coding agent.

When the user requests something, determine the correct function to call.

Available operations:
- List files and directories
- Read file contents
- Write or overwrite files
- Execute Python files with optional arguments

You MUST work step-by-step, using tools as needed.
All file paths MUST be relative to the working directory.
Do NOT include the working directory in tool calls.
"""

WORKING_DIRECTORY = "calculator"


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = dict(function_call_part.args or {})

    # Insert working directory
    function_args = {
        "working_directory": WORKING_DIRECTORY,
        **function_args,
    }

    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        result = function_map[function_name](**function_args)
    except Exception as e:
        result = f"Error executing {function_name}: {str(e)}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Gemini Agent")
    parser.add_argument("prompt", type=str)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    messages = [
        types.Content(role="user", parts=[types.Part(text=args.prompt)])
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file,
        ]
    )

    for _ in range(20):  # max iterations
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        candidates = response.candidates or []
        saw_fc = False
        final_text = None

        for cand in candidates:
            content = cand.content
            if not content:
                continue

            parts = content.parts or []
            messages.append(types.Content(role="model", parts=parts))

            for part in parts:
                fc = getattr(part, "function_call", None)
                if fc:
                    saw_fc = True
                    call_result = call_function(fc, verbose=args.verbose)
                    messages.append(
                        types.Content(role="user", parts=call_result.parts)
                    )
                else:
                    if part.text:
                        final_text = part.text

        if final_text and not saw_fc:
            print("Final response:")
            print(final_text)
            break

    else:
        print("Reached max iterations (20).")


if __name__ == "__main__":
    main()
