# ChatGPT Saved Memories

This folder holds memories extracted from ChatGPT and structured for use in Memspan. Memories are essentially a **cut & paste** from ChatGPT Settings → Memory, but you can also add any additional memories you want to include.

## Overview

**Memories** are saved facts and preferences that ChatGPT remembers about you:
- Biographical facts
- Preferences (coding style, communication, tools)
- Important relationships
- Recurring themes and patterns

**Note:** The OpenAI API does **not** support memory features—this is only available through the ChatGPT web interface.

## Files

- **`memories.md`** - Raw memories copied from ChatGPT (or manually added). This is your source file.
- **`memories-example.md`** - Example showing the format of raw memories
- **`export_prompt.md`** - Prompt to structure and enrich memories with metadata
- **`memories_export.md`** / **`memories_export.json`** - Structured output (generated from `memories.md` using `export_prompt.md`)

## How It Works

### Step 1: Extract Raw Memories

1. Open ChatGPT Settings → Personalization & Memory
2. View your saved memories
3. **Copy all the text** and paste it into `memories.md`
4. You can also add any additional memories you want to include

### Step 2: Structure the Memories (Optional)

The `export_prompt.md` adds structure and metadata to your raw memories:

- Adds IDs, summaries, and details
- Extracts topics, entities, and dates
- Creates both JSON and Markdown formats

To use:

1. Copy the prompt from `export_prompt.md`
2. Paste your `memories.md` content into ChatGPT/Claude
3. Save the structured output as `memories_export.md` or `memories_export.json`

### Step 3: Save to Memspan

Save the structured export to:

```text
claude-memory/memory/chatgpt/memories_export.md
```

## Usage

- Load raw memories: Use `memories.md` directly as context
- Load structured memories: Use `memories_export.md` (recommended for better structure)
- Cherry-pick: Copy specific memories into project contexts

## Notes

- Keep sensitive content in mind; only include what you want Claude to see
- The raw `memories.md` can be simple text—one memory per line or paragraph
- The structured export adds organization but isn't required

