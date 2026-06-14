"""Tool: list_directory — lists contents of a directory on the filesystem."""

from pathlib import Path

# OpenAI-compatible function definition for the API
definition = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List the contents of a directory at the specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path of the directory to list.",
                }
            },
            "required": ["path"],
        },
    },
}


def handler(path: str) -> str:
    """List the contents of a directory and return a formatted string."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: Path does not exist: {p}"
        if not p.is_dir():
            return f"Error: Not a directory: {p}"

        items = []
        for entry in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if entry.is_dir():
                items.append(f"  📁  {entry.name}/")
            else:
                size = entry.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024**2:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / 1024**2:.1f} MB"
                items.append(f"  📄  {entry.name}  ({size_str})")

        result = f"Contents of {p}:\n" + "\n".join(items) if items else f"Directory is empty: {p}"
        return result
    except PermissionError as e:
        return f"Error: Permission denied: {e}"
    except Exception as e:
        return f"Error: {e}"
