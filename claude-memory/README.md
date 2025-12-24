# Claude Memory Starter (File-Only, No MCP/Vector)

This subdirectory is a minimal, opt-in setup for loading context into Claude (CLI or Claude Code) from any working directory. It keeps data out of the control file and uses a small wrapper script to attach the right files.

**Note:** This system is **independent** of Claude's built-in memory feature. It provides file-based, portable memory that you control and can use across different LLM systems.

## Layout
```
claude-memory/
  README.md                # This file
  CLAUDE.md                # Data-free control file (instructions only)
  bin/cc-memspan           # Wrapper script to launch claude with chosen contexts
  memory/
    identity/              # Put or symlink condensed identity here
    chatgpt/               # Structured ChatGPT memories here
    projects/              # Project contexts, conversations, projects index
```

## Quick start
1) Ensure `claude` CLI is installed and on PATH.  
2) Put or symlink your files:
   - Identity: `claude-memory/memory/identity/core-identity.md` (or `.json`). Fallback: `identity-archive/core-identity.json` (auto-loaded if present).
   - ChatGPT memories (structured only): `claude-memory/memory/chatgpt/memories_export.md`
   - Projects: `claude-memory/memory/projects/<project>/context.md` (optional), `conversations.json` (optional)
   - Projects index (global): `claude-memory/memory/projects/projects.json` (optional)
3) Run a session with the wrapper (examples below).

## Wrapper script: `bin/cc-memspan`
The script builds absolute paths so it works from any directory, then injects selected files into the Claude session via `--append-system-prompt` (the CLI does not support `--add-context`).

Common invocations:
- Minimal (control file only):  
  `bash claude-memory/bin/cc-memspan`
- Add identity:  
  `bash claude-memory/bin/cc-memspan --identity`
- Add structured memories:  
  `bash claude-memory/bin/cc-memspan --memories`
- Project bundle (context/conversations when present):  
  `bash claude-memory/bin/cc-memspan --project your_project_name`
- Everything for a project (identity + structured memories + project bundle):  
  `bash claude-memory/bin/cc-memspan --full your_project_name`
- Add projects index (global list):  
  `bash claude-memory/bin/cc-memspan --projects-index`
- Use a saved current project (optional file `memory/current-project`):  
  `echo mindjot > claude-memory/memory/current-project`  
  `bash claude-memory/bin/cc-memspan --use-current`

Pass extra args to claude after `--`, e.g. `... -- "help me refactor X"`.

## How it stays opt-in
- `CLAUDE.md` contains no identity or memory content—only instructions and pointers.
- You choose which files to attach per run (`--identity`, `--memories`, `--project`, `--projects-index`, `--full`). They are inlined into a system prompt block for the session.
- If a requested file is missing, the script warns and continues without it.

## Working inside other projects
- Because the script uses absolute paths anchored to this folder, it’s safe to run from any repo or subdirectory.
- If another project has its own `CLAUDE.md`, that doesn’t interfere; you are explicitly adding contexts from here.

## Files to supply (or symlink)
- `memory/identity/core-identity.md`: condensed identity (no secrets in repo unless you intend to).
- `memory/chatgpt/memories_export.md`: structured ChatGPT memories (only file expected here).
- `memory/projects/<project>/context.md`: optional per-project context.
- `memory/projects/<project>/conversations.json`: optional detailed history per project.
- `memory/projects/projects.json`: optional global projects list.

## How It Works

### Context Loading

The `cc-memspan` script:
1. Reads selected context files (identity, memories, projects)
2. Combines them into a system prompt block
3. Launches Claude with `--append-system-prompt`

Context is sent with every message, so Claude has access to your identity and memories throughout the session.

### CLAUDE.md Instructions

`CLAUDE.md` is a **data-free control file** that contains:
- Instructions for Claude about where context files live
- Memory precedence rules (Claude memories > ChatGPT memories > identity)
- Memory saving behavior configuration
- Instructions for loading historical data on-demand

**Key behaviors:**
- Claude does **not** assume identity or memories unless files are explicitly loaded
- If asked about prior decisions/history without context, Claude will ask whether to load specific files
- Historical conversations are loaded ad-hoc when needed (not automatically)

### Memory Saving Behavior

Claude can proactively save memories during sessions to `memory/claude/entries/`. The system supports:
- **`ask-first`** (current): Claude asks before saving
- **`save-and-notify`** (planned): Claude saves and mentions it
- **`silent`** (planned): Claude saves without mention

**What triggers memory saving:**
- New biographical facts or corrections
- Stated preferences or changes to preferences
- Significant insights or self-observations
- Goal updates or life context changes
- Decisions or commitments made during conversation
- Explicit user request ("remember this", "save this")

See `memory/claude/README.md` for full documentation on the memory system.

## How This Differs from Claude's Default Memory

**Claude's Built-in Memory:**
- Managed by Anthropic, stored on their servers
- Automatic and opaque (you don't see what's stored)
- Platform-locked to Claude/Anthropic
- Not portable to other LLMs or systems
- Limited control over what gets saved

**Memspan's File-Based Memory:**
- **You control everything** - files on your system
- **Transparent** - you can see and edit all memories
- **Portable** - standard formats (JSON, Markdown) work with any LLM
- **Selective** - you choose what to load per session
- **Extractable** - can migrate to other systems easily
- **Version-controlled** - can track changes in git
- **Independent** - doesn't interfere with Claude's built-in memory

## Advantages of This Approach

### 1. **Portability Across LLMs**
- Standard formats (JSON, Markdown) work with any LLM system
- Not locked to Claude or Anthropic
- Can migrate to GPT-4, local models, or future LLMs
- Your data stays with you

### 2. **Full Control & Transparency**
- See exactly what's in your memory files
- Edit, update, or remove memories directly
- No black-box storage
- Version control friendly

### 3. **Selective Loading**
- Load only what you need per session
- Control token usage by choosing context
- Lightweight sessions when you don't need full history
- Ad-hoc loading of historical data when needed

### 4. **Data Ownership**
- Files on your system, not in the cloud
- Export and backup easily
- No vendor lock-in
- Can be encrypted, synced, or archived as you choose

### 5. **Future-Proof**
- Works with current and future LLM systems
- Can be integrated into custom agents
- Compatible with MCP servers, vector databases, or other tools
- Foundation for digital twins or persistent AI assistants

### 6. **Extensibility**
- Add custom context files easily
- Integrate with other tools (notion, obsidian, etc.)
- Build on top of the file structure
- No API limitations

## Notes and Guidance

- If you prefer shorter commands, add an alias in your shell:  
  `alias ccms='bash YOUR_BASE_DIR/memspan/claude-memory/bin/cc-memspan'`
- Set `CLAUDE_CMD` env var if your CLI is named differently (default: `claude`).
- Dynamic conversation retrieval: without MCP, keep it manual. Attach `conversations.json` (project or global) when you need history; omit when you don't. If you want automatic retrieval later, we can add MCP-backed search, but stay file-only for this pilot.
- CLI context note: Files are injected as text via `--append-system-prompt`; large files increase prompt size—use selectively.



