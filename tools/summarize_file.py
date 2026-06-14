"""Tool: summarize_file — reads a file and returns its content for summarization."""

from . import read_file


definition = {
    "type": "function",
    "function": {
        "name": "summarize_file",
        "description": "Read a file and summarize its contents. Provide the path to the file you want summarized.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path of the file to summarize.",
                },
            },
            "required": ["path"],
        },
    },
}


def handler(path: str) -> str:
    """Read a file and return its content with a request for summarization."""
    content = read_file.handler(path)
    # The agent will see this and produce a summary in its response
    return f"Please summarize the following file content:\n\n{content}"
