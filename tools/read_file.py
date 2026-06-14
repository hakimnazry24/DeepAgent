"""Tool: read_file — reads and returns the content of a file."""

from pathlib import Path


definition = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file at the specified path. Returns the file content along with line count and size.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path of the file to read.",
                },
            },
            "required": ["path"],
        },
    },
}


def handler(path: str) -> str:
    """Read a file and return its contents with metadata."""
    try:
        p = Path(path).expanduser().resolve()

        if not p.exists():
            return f"Error: File does not exist: {p}"
        if not p.is_file():
            return f"Error: Not a file: {p}"

        size = p.stat().st_size
        content = p.read_text(encoding="utf-8")
        lines = content.count("\n") + (1 if content else 0)

        # Truncate at 5000 lines to avoid overwhelming the model
        MAX_LINES = 5000
        if lines > MAX_LINES:
            truncated = True
            content_lines = content.splitlines()[:MAX_LINES]
            content = "\n".join(content_lines)
            content += f"\n\n... [truncated — file has {lines} lines, showing first {MAX_LINES}]"
        else:
            truncated = False

        summary = f"📄 {p.name}  ({size:,} bytes, {lines} lines{' (truncated)' if truncated else ''})"
        separator = "─" * 50

        return f"{summary}\n{separator}\n{content}\n{separator}"
    except PermissionError as e:
        return f"Error: Permission denied: {e}"
    except UnicodeDecodeError:
        size = p.stat().st_size
        return f"⚠️  Binary file ({size:,} bytes) — cannot display as text: {p}"
    except Exception as e:
        return f"Error: {e}"
