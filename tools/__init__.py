"""
Tools package — each module exports:
  - `definition`: the OpenAI-compatible tool schema dict
  - `handler`: the callable that executes the tool
"""

from . import list_directory
from . import create_file
from . import read_file

# Collect all tool definitions for the API
definitions = [
    list_directory.definition,
    create_file.definition,
    read_file.definition,
]

# Dispatch map: tool name → handler function
dispatch = {
    "list_directory": list_directory.handler,
    "create_file": create_file.handler,
    "read_file": read_file.handler,
}
