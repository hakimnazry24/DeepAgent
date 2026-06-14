# DeepSeek Agent

A lightweight AI agent powered by the DeepSeek API that can list directories and write code to files.

## Features

- **📂 List directories** — Explore the contents of any directory on your filesystem
- **✍️ Write code/files** — Ask for code and the agent will save it directly to a new file
- **🔄 Streaming responses** — See the agent's reply as it's generated
- **🔧 Extensible tool system** — Add new capabilities by dropping a file into `tools/`

## Requirements

- Python 3.10+
- A DeepSeek API key

## Setup

1. **Clone the repo** and navigate into the project folder.

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key:**

   ```powershell
   # Windows (PowerShell)
   set DEEPSEEK_API_KEY=your_key_here
   ```

   Or create a `.env` file in the project root:

   ```env
   DEEPSEEK_API_KEY=your_key_here
   ```

## Usage

```bash
python deepseek_chat.py
```

Type your requests at the `You:` prompt. The agent can:

| You say... | It does |
|---|---|
| *"List the files in the current directory"* | Calls `list_directory` |
| *"What's in C:\Projects?"* | Calls `list_directory` |
| *"Write a Python script that prints hello"* | Generates the code and calls `create_file` |
| *"Create a React component called Button"* | Writes the component to a file |
| *"Tell me a joke"* | ❌ Refuses — outside its capabilities |

### Exit

Type `quit`, `exit`, or `q`, or press **Ctrl+C** to stop.

## Project Structure

```
├── deepseek_chat.py          # Main agent — orchestrates the chat loop
├── requirements.txt          # Python dependencies
├── README.md
└── tools/
    ├── __init__.py            # Registers all tool definitions + dispatch
    ├── list_directory.py      # Tool: list directory contents
    └── create_file.py         # Tool: create a file with content
```

## Adding a New Tool

1. Create `tools/your_tool.py` with:
   - `definition` — the OpenAI-compatible function schema
   - `handler(**kwargs)` — the Python function that runs the tool

2. Register it in `tools/__init__.py`:

   ```python
   from . import your_tool

   definitions = [
       list_directory.definition,
       create_file.definition,
       your_tool.definition,
   ]

   dispatch = {
       "list_directory": list_directory.handler,
       "create_file": create_file.handler,
       "your_tool": your_tool.handler,
   }
   ```

No changes needed in `deepseek_chat.py` — it automatically picks up whatever is in `tools/__init__.py`.

## Model

Uses DeepSeek's API via the OpenAI-compatible SDK. The model is configured as `deepseek-v4-pro` in the streaming response handler.
