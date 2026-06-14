"""Tool: create_file — creates a new file with the given content."""

from pathlib import Path


definition = {
    "type": "function",
    "function": {
        "name": "create_file",
        "description": "Create a new file at the specified path with the given content. Creates parent directories if they don't exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path where the file should be created.",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write into the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
}


def handler(path: str, content: str) -> str:
    """Create a new file with the given content. Returns a status message."""
    try:
        p = Path(path).expanduser().resolve()

        if p.exists():
            return f"Error: File already exists: {p}"

        # Create parent directories if needed
        p.parent.mkdir(parents=True, exist_ok=True)

        p.write_text(content, encoding="utf-8")
        return f"✅ File created successfully: {p} ({len(content)} bytes written)"
    except PermissionError as e:
        return f"Error: Permission denied: {e}"
    except Exception as e:
        return f"Error: {e}"
