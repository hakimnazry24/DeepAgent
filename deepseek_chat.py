"""
DeepSeek Agent Chat
An agent that can list directories and chat with you.
Type 'quit', 'exit', or 'q' to stop the program.
"""

from openai import OpenAI
import os
import sys
import json
from dotenv import load_dotenv

from tools import definitions as TOOLS, dispatch as TOOL_DISPATCH

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    print("Error: DEEPSEEK_API_KEY environment variable is not set.")
    print("Set it with: set DEEPSEEK_API_KEY=your_api_key_here")
    sys.exit(1)

MODEL = "deepseek-v4-pro"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1",
)

# ─── System Prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a code generation agent. You can ONLY do the following:

1. List the contents of a directory (`list_directory`)
2. Read the contents of a file (`read_file`)
3. Create a new file with content (`create_file`)

**CRITICAL — NEVER guess or assume parameter values.**
Before calling any tool, you MUST ask the user for every required parameter that is not explicitly specified:

- `list_directory` → ask "Which directory would you like me to list?"
- `read_file` → ask "Which file would you like me to read?"
- `create_file` → ask "What file path should I create?" AND "What content should I write?"

Do NOT proceed with a tool call until the user has provided all required information.
Do NOT use default values (like current directory ".") unless the user explicitly says so.
Do NOT make up file names, paths, or content on your own.

Other rules:
- You CANNOT answer general questions, explain concepts, provide information, or do anything outside of the three tools above.
- If a user asks you to do something other than these three actions, politely refuse.
- Be concise and direct.

Your ONLY available tools:
- `list_directory(path)` — List the contents of a directory
- `read_file(path)` — Read the contents of a file
- `create_file(path, content)` — Create a new file with the given content"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

print("=" * 60)
print("  🤖 DeepSeek Agent — I can list directories for you!")
print("  Type 'quit', 'exit', or 'q' to stop.")
print("=" * 60)


# ─── LLM Helpers ────────────────────────────────────────────────────────────


def call_llm() -> tuple[str | None, list | None, str | None]:
    """Call the LLM and return (text_content, tool_calls, reasoning_content)."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        temperature=0.7,
    )
    msg = response.choices[0].message
    # DeepSeek v4 pro returns reasoning_content in model_extra for thinking mode
    reasoning = msg.model_extra.get("reasoning_content") if msg.model_extra else None
    return msg.content, msg.tool_calls, reasoning


def process_tool_calls(tool_calls) -> list[dict]:
    """Execute tool calls and return result messages to feed back."""
    results = []
    for tc in tool_calls:
        func_name = tc.function.name
        try:
            args = json.loads(tc.function.arguments)
        except json.JSONDecodeError:
            args = {}

        print(f"\n  🛠  Calling tool: {func_name}({json.dumps(args)})")

        handler = TOOL_DISPATCH.get(func_name)
        result = handler(**args) if handler else f"Error: Unknown tool '{func_name}'"

        print(f"  {'─' * 50}")
        for line in result.split("\n"):
            print(f"     {line}")
        print(f"  {'─' * 50}")

        results.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result,
        })
    return results


def stream_response() -> tuple[str, str | None]:
    """Stream the assistant's final response and return (full_text, reasoning_content)."""
    print("\n🤖 Agent: ", end="", flush=True)
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        temperature=0.7,
    )
    full = ""
    reasoning = ""
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            full += delta.content
        if delta.model_extra:
            rc = delta.model_extra.get("reasoning_content")
            if rc:
                reasoning += rc
    print()
    return full, reasoning or None


# ─── Main Loop ──────────────────────────────────────────────────────────────

try:
    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Agent loop — keep calling the LLM until we get a text response
        while True:
            content, tool_calls, reasoning = call_llm()

            if tool_calls:
                assistant_msg = {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": [tc.model_dump() for tc in tool_calls],
                }
                if reasoning:
                    assistant_msg["reasoning_content"] = reasoning
                messages.append(assistant_msg)
                messages.extend(process_tool_calls(tool_calls))
                continue

            if content:
                full, stream_reasoning = stream_response()
                assistant_msg = {"role": "assistant", "content": full}
                final_reasoning = stream_reasoning or reasoning
                if final_reasoning:
                    assistant_msg["reasoning_content"] = final_reasoning
                messages.append(assistant_msg)
            break

except KeyboardInterrupt:
    print("\n\nGoodbye!")
    sys.exit(0)
