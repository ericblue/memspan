# Session Context Controls (Data-Free)

- This file carries **no identity or memory content**. It only describes what optional context files exist.
- Load it when you want Claude to know where identity, memories, and project context live; skip it when you want a clean session.

## Optional context files (add explicitly)

### Identity
- Identity (condensed): `memory/identity/core-identity.md` (or `.json`)

### Memories
- **Claude memories (active, evolving):** `memory/claude/index.json` and `memory/claude/entries/*.md`
- ChatGPT memories (static archive): `memory/chatgpt/memories_export.md`

### Projects
- Project context (optional): `memory/projects/<project>/context.md`
- Project conversations (optional): `memory/projects/<project>/conversations.json`
- Projects index (optional): `memory/projects/projects.json`

## Behavior instructions for Claude

### General
- Do **not** assume identity or memories unless the corresponding file is included.
- If asked about prior decisions/history without context, ask whether to load a specific file.

### Memory Precedence (when conflicts exist)
1. **Claude memories** (`memory/claude/`) take precedence over ChatGPT memories
2. **Newer entries** take precedence over older entries
3. **Explicit corrections** take precedence over inferred information
4. Overall priority: project context → Claude memories → identity → ChatGPT memories

### Memory Saving Behavior

Claude can proactively save memories during sessions. The current notification mode is defined in `memory/claude/index.json`.

| Mode | Behavior |
|------|----------|
| `ask-first` | Claude asks before saving **(current)** |
| `save-and-notify` | Claude saves and mentions it (planned) |
| `silent` | Claude saves without mention (planned) |

**What triggers memory saving:**
- New biographical facts or corrections
- Stated preferences or changes to preferences
- Significant insights or self-observations
- Goal updates or life context changes
- Decisions or commitments made during conversation
- Explicit user request ("remember this", "save this")

**When saving memories:**

1. **If `memory/claude/index.json` doesn't exist**, create it with this structure:
   ```json
   {
     "config": {
       "notification_mode": "ask-first",
       "notification_modes_available": ["ask-first", "save-and-notify", "silent"],
       "notes": "Initial setup"
     },
     "entries": []
   }
   ```

2. **If `memory/claude/entries/` directory doesn't exist**, create it.

3. **When creating a new memory entry:**
   - Create a markdown file: `memory/claude/entries/YYYY-MM-DD-slug.md`
   - Add entry to `index.json` with metadata:
     - `id`: "YYYY-MM-DD-slug"
     - `file`: "entries/YYYY-MM-DD-slug.md"
     - `created`: "YYYY-MM-DD"
     - `type`: One of `fact`, `insight`, `context`, `correction`, `preference`
     - `topics`: Array of relevant topic tags
     - `summary`: One-line summary
     - `source`: "conversation" (or "explicit-request" if user asked)
     - `supersedes`: null (or ID if replacing an entry)

4. **Read existing `index.json` first** to check for duplicates and get current config. If the file doesn't exist, use `ask-first` as the default mode.

See `memory/claude/README.md` for full documentation and `memory/claude/index-example.json` for a complete example.



