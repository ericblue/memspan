# Project Contexts

Create a subfolder per project and drop context files there.

## Files Per Project

- **`context.md`** - **Primary project context** (lightweight, current state) - **Recommended for most sessions**
- **`conversations.json`** - Full conversation history (load ad-hoc when needed) - **Higher token usage**

## Global File

- **`projects.json`** - List of projects and metadata (generated from `export-chatgpt-conversations`)

## Example Layout

```
memory/projects/
├── projects.json                    ← From export-chatgpt-conversations
├── projects-example.json            ← Example format reference
├── README.md                        ← This file
└── your_project_name/               ← Project subdirectory (create as needed)
    ├── context.md                   ← Primary context (lightweight, ~2-5KB)
    └── conversations.json           ← Full history (load ad-hoc, can be large)
```

## Setting Up Project Files

### 1. Generate context.md (Recommended)

**`context.md` is the primary project context** - use it for most sessions to keep token usage low.

**Option A: Generate from conversations (recommended)**
1. Export project conversations:
   ```bash
   python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-project "Project Name" -o temp.json
   ```
2. Use the prompt in `export-chatgpt-conversations/generate-context-prompt.md` with Claude to generate `context.md`
3. Save to `memory/projects/<project>/context.md`

**Option B: Create manually**
- Write a concise overview (2-5KB) covering:
  - Project purpose and current status
  - Architecture and design
  - Active goals and priorities
  - Key decisions
  - Current state and next steps

**Note:** Future release will automate context.md generation from conversations.

### 2. Export conversations.json (Optional, for ad-hoc use)

1. Export a project using `export-chatgpt-conversations`
2. Copy the output to `memory/projects/<project>/conversations.json`
3. **Use sparingly** - only load when you need to reference specific historical conversations

## Usage Pattern

- **Most sessions**: Load `context.md` only (via `--project`)
- **Deep historical work**: Load `conversations.json` ad-hoc when needed
- **Both together**: Only if you need current state + specific historical details

Keep `context.md` concise (2-5KB) and focused on current state. Update it as the project evolves.




