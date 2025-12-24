# Memspan Quick Start Guide

> Get up and running with Memspan in minutes

This guide will help you extract your identity, memories, and conversations from ChatGPT and load them into Claude Code sessions.

## Table of Contents

1. [Overview](#overview)
2. [Data Types from Other LLMs](#data-types-from-other-llms)
3. [Extracting Data](#extracting-data)
4. [Using cc-memspan](#using-cc-memspan)
5. [Creating Aliases](#creating-aliases)

---

## Overview

**Memspan** is a file-system based memory archive that helps you maintain continuity across AI assistant sessions. It solves a fundamental problem: **LLMs don't remember across sessions**, and platform-specific memory features (like ChatGPT's memory) don't transfer to other tools.

### How Memspan Works

Memspan uses a **three-tier memory model**:

1. **Core Identity** (~2-4KB): Always-available personal context
   - Who you are, your preferences, communication style
   - Stored in `claude-memory/memory/identity/core-identity.json`

2. **Project/Framework Memory** (~10-50KB per domain): Session-selectable deep context
   - Project-specific context, decisions, conversation history
   - Stored in `claude-memory/memory/projects/<project-name>/`

3. **Historical Archive**: Indexed, retrieved on-demand
   - Full conversation history, indexed for search
   - Stored in `claude-memory/memory/chatgpt/` and project directories

### Data Flow

```
ChatGPT (Web Interface)
    ↓ Extract
Identity, Memories, Conversations
    ↓ Organize
Memspan Memory Files
    ↓ Load
Claude Code Sessions
```

### Key Principles

- **File-based**: No databases, just files you control
- **Portable**: Works across different LLM tools
- **Selective**: Load only what you need per session
- **Opt-in**: You choose what context to load

---

## Data Types from Other LLMs

Memspan currently supports extracting three types of data from **OpenAI ChatGPT**:

### 1. Identity

**What it is:** A comprehensive personal profile including:
- Personal information (name, location, career)
- Personality traits and cognitive styles
- Communication preferences
- Technology stack and tools
- Professional context
- Goals and motivations
- Values and philosophy
- And much more (18 major sections total)

**Source:** ChatGPT's internal memory and conversation history

**Format:** Structured JSON with deeply nested sections

**Size:** Full archive can be large; condensed version ~2-4KB

### 2. Memories

**What it is:** Saved facts and preferences that ChatGPT remembers about you:
- Biographical facts
- Preferences (coding style, communication, tools)
- Important relationships
- Recurring themes and patterns

**Source:** ChatGPT Settings → Memory (web interface only)

**Format:** Markdown or structured JSON

**Size:** Varies based on how many memories you've saved

**Note:** The OpenAI API does **not** support memory features—this is only available through the web interface.

### 3. Conversations & Projects

**What it is:** 
- **Conversations**: Full chat history with messages
- **Projects**: ChatGPT Projects (organized conversation groups) with metadata

**Source:** 
- ChatGPT Data Export (conversations)
- ChatGPT API (project metadata—not included in standard export)

**Format:** JSON with conversation trees and project mappings

**Size:** Can be very large (thousands of conversations)

**Note:** The standard ChatGPT export doesn't include project metadata—you need separate tools to correlate conversations with projects.

---

## Extracting Data

This section covers how to extract each type of data and where it gets saved in Memspan.

### Extracting Identity

Identity extraction is a **manual process** using a specialized prompt in ChatGPT's web interface.

#### Why Manual?

- **No API Support**: The OpenAI API doesn't support memory features like the web interface
- **User Control**: You decide when and how to extract your identity
- **Quality Review**: You can review and refine the output before saving

#### Step-by-Step Process

1. **Enable ChatGPT Memory**:
   - Log in to ChatGPT (chat.openai.com)
   - Go to Settings → Personalization & Memory
   - Ensure memory is enabled

2. **Run the Identity Prompt**:
   - Open a new ChatGPT conversation
   - Copy the entire prompt from `identity-archive/identity-archive-prompt.md`
   - Paste it into ChatGPT and send

3. **Review the Output**:
   - ChatGPT will generate a comprehensive JSON profile
   - Review it for accuracy (hallucinations are possible)
   - The output includes 18 major sections with rich details
   - **Tip:** Compare with `core-identity-example.json` to see the expected structure

4. **Save to Memspan**:
   ```bash
   # Copy the JSON output and save it to:
   ./claude-memory/memory/identity/core-identity.json
   ```

#### What You Get

The identity JSON includes:
- `personal_info` - Name, location, career, companies, life events
- `personality_traits` - Cognitive style, creativity, leadership, ambition
- `communication_style` - Tone, collaboration preferences
- `technology_and_tools` - Programming languages, frameworks, projects
- `profession_and_work` - Career trajectory, work philosophy
- `goals_and_motivations` - Short-term and long-term goals
- `fitness_and_health` - Health metrics, training strategies
- `interests_and_learning` - Intellectual pursuits, learning methods
- `values_and_philosophy` - Privacy views, economic beliefs, ethics
- `emotional_and_cognitive_patterns` - Stress response, thinking styles
- `relationships_and_social_dynamics` - Team roles, collaboration beliefs
- `legacy_and_identity` - Long-term vision, desired impact
- `memories_and_stories` - Personal stories with emotional context
- `daily_routines_and_habits` - Morning/evening rituals, productivity practices
- `tools_and_systems_used` - Productivity tools, development environments
- `environmental_preferences` - Work settings, workspace setup
- `self_reflection_and_growth` - Introspection approaches, growth systems
- `personality_type_assessments` - MBTI, Big Five, CliftonStrengths

#### Output Quality

The quality depends on:
- **Interaction History**: More conversations = richer profile
- **Memory Enablement**: Memory must be enabled and active
- **Conversation Depth**: Detailed conversations lead to comprehensive profiles

**Important:** Always review the output for accuracy—hallucinations are possible.

#### File Location

```
claude-memory/
└── memory/
    └── identity/
        ├── core-identity.json         ← Save your identity here
        └── core-identity-example.json ← Example structure (fake data)
```

**Example File:** See `claude-memory/memory/identity/core-identity-example.json` for a complete example of the expected JSON structure with placeholder data. This can help you understand the format and depth of information to include.

### Extracting Memories

Memories are saved facts and preferences that ChatGPT remembers about you. The extraction process is simple: **cut & paste** from ChatGPT, then optionally structure them.

#### Step-by-Step Process

1. **Copy from ChatGPT**:
   - Log in to ChatGPT (chat.openai.com)
   - Go to Settings → Personalization & Memory
   - View your saved memories
   - **Copy all the text** and paste it into `export-chatgpt-memories/memories.md`

2. **Add Additional Memories** (Optional):
   - You can also manually add any additional memories you want to include
   - Just add them to the same `memories.md` file

3. **Structure the Memories** (Optional):
   - The `export_prompt.md` adds structure and metadata to your raw memories
   - Copy the prompt from `export-chatgpt-memories/export_prompt.md`
   - Paste your `memories.md` content into ChatGPT/Claude
   - Save the structured output

4. **Save to Memspan**:
   ```bash
   # Save the structured export to:
   ./claude-memory/memory/chatgpt/memories_export.md
   ```

#### What You Get

Raw memories (`memories.md`):
- Simple text format
- One memory per line or paragraph
- Can be used directly as context

Structured memories (`memories_export.md`):
- Organized with IDs and summaries
- Includes topics, entities, and dates
- Better organized for loading as context

#### Example File

See `export-chatgpt-memories/memories-example.md` for an example of what raw memories look like when copied from ChatGPT.

#### File Location

```
claude-memory/
└── memory/
    └── chatgpt/
        └── memories_export.md    ← Save structured memories here
```

**Note:** The OpenAI API does **not** support memory features—this is only available through the ChatGPT web interface.

### Extracting Conversations & Projects

This process exports your ChatGPT conversations and optionally correlates them with Projects (if you use ChatGPT Projects). The process has two parts:

1. **Export conversations** from ChatGPT (manual download)
2. **Extract project metadata** from Chrome DevTools (if you use Projects)
3. **Correlate** conversations with projects

#### Step 1: Export Conversations from ChatGPT

ChatGPT allows you to export all your data as a zip file:

1. Log in to ChatGPT (chat.openai.com)
2. Go to **Settings → Data Controls → Export Data**
3. Click **Request Data Export** or similar button
4. You'll receive an email with a download link (may take a few minutes)
5. Download and extract the zip file

**Important:** The zip file contains `conversations.json` - this is your complete conversation history. Extract this file and save it as `conversations.json` in your working directory.

**Note:** The official export does **not** include project metadata. If you use ChatGPT Projects, you'll need Step 2 to correlate conversations with projects.

#### Step 2: Extract Project Metadata (If You Use Projects)

If you use ChatGPT Projects, you need to extract project metadata separately because it's not included in the official export. This uses Chrome DevTools to capture an API call.

**Detailed Chrome DevTools Steps:**

1. **Open ChatGPT in Chrome**:
   - Log in to chat.openai.com
   - Make sure you're on the main chat interface

2. **Open Chrome DevTools**:
   - Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows/Linux)
   - Or right-click the page → **Inspect**

3. **Open the Network Tab**:
   - Click the **Network** tab in DevTools
   - Make sure the network log is recording (red circle should be active, or click the record button)

4. **Trigger the Projects API Call**:
   - Click on **Projects** in the ChatGPT sidebar (or refresh the page)
   - This will generate network requests

5. **Find the Projects Request**:
   - In the Network tab, look for a request to `/backend-api/gizmos/snorlax/sidebar`
   - You can filter by typing "gizmos" or "snorlax" in the filter box
   - The request should be a `GET` request

6. **Copy as cURL**:
   - Right-click on the `/gizmos/snorlax/sidebar` request
   - Select **Copy → Copy as cURL** (or **Copy → Copy as cURL (bash)**)
   - This copies the full cURL command with all headers and authentication

7. **Save the cURL Command**:
   - Paste the copied cURL command into a file: `export-chatgpt-conversations/curl.txt`
   - Or save it anywhere and reference it with `--curl-file`

**What This Does:**
- The cURL command contains your authentication cookies and headers
- The script replays this API call to get your projects list
- This is the same API call ChatGPT uses to populate the Projects sidebar

#### Step 3: Run the Export Scripts

**Extract Projects Metadata:**

```bash
cd export-chatgpt-conversations
python3 chatgpt_projects_dump.py --curl-file curl.txt
```

This creates:
- `projects.json` - Cleaned project metadata
- `projects_raw.json` - Full API responses (for debugging)

**Correlate Conversations with Projects:**

```bash
# Make sure conversations.json is in the same directory or specify the path
python3 chatgpt_project_conversations.py export
```

This correlates conversations with projects using the `gizmo_id` field and creates:
- Project-to-conversation mappings
- Categorized exports (project conversations, regular conversations, orphaned projects)

**Common Commands:**

```bash
# List all projects
python3 chatgpt_project_conversations.py list-projects

# Export all with full message content (warning: large files)
python3 chatgpt_project_conversations.py export --with-messages

# Export a specific project
python3 chatgpt_project_conversations.py export-project "Project Name"
```

#### What You Get

- **Project conversations**: Conversations linked to active projects
- **Regular conversations**: Standard ChatGPT chats without projects
- **Orphaned conversations**: Conversations from deleted projects
- **Project metadata**: Names, creation dates, memory settings

**Note:** The export scripts create `conversations.json` files, but you'll need to:
1. Copy exported project conversations to `memory/projects/<project>/conversations.json` if you want to use `--project`
2. Manually create `context.md` in each project directory (see project context section below)

#### File Locations

```
export-chatgpt-conversations/
├── conversations.json          ← From ChatGPT data export (.zip file)
├── projects.json               ← Generated from API call (save to memory/projects/)
└── project_conversations.json  ← Generated correlation output
```

**Important:** After generating `projects.json`, save it to `claude-memory/memory/projects/projects.json` to enable the lightweight `--projects-index` option in `cc-memspan`.

**Note:** If you don't use ChatGPT Projects, you can skip Step 2 and just use `conversations.json` directly. The correlation script will still work and categorize your conversations.

---

## Using cc-memspan

The `cc-memspan` script is a wrapper that loads your identity, memories, and project context into Claude Code sessions. It works from any directory and uses absolute paths. This is part of the memspan project for portable, file-based memory.

### Installation

Ensure the `claude` CLI is installed and on your PATH:

```bash
# Check if claude is available
which claude

# If not installed, install it (see Claude Code documentation)
```

### Basic Usage

```bash
# From any directory, use the full path:
bash ~/path/to/memspan/claude-memory/bin/cc-memspan [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--identity` | Load identity from `memory/identity/core-identity.json` (or `.md`) |
| `--memories` | Load ChatGPT memories from `memory/chatgpt/memories_export.md` |
| `--project NAME` | Load project bundle (context.md, conversations.json) |
| `--projects-index` | Load global projects list from `memory/projects/projects.json` |
| `--full NAME` | Shorthand: `--identity --memories --project NAME` |
| `--use-current` | Use project from `memory/current-project` file |
| `--dry-run` | Print the command without running |
| `-h, --help` | Show help message |

### Common Patterns

#### Minimal Load (Recommended Starting Point)

```bash
bash claude-memory/bin/cc-memspan --identity --memories
```

**Recommended for most sessions.** Loads your core identity and saved ChatGPT memories. This is the essential context without project overhead.

#### Lightweight Project Awareness

```bash
bash claude-memory/bin/cc-memspan --identity --memories --projects-index
```

Adds project awareness by loading `projects.json` (generated by `export-chatgpt-conversations`). Claude knows about your projects (names, metadata) but **without** full conversation history—much lower token usage.

**Note:** This requires `projects.json` to be saved to `claude-memory/memory/projects/projects.json` from your conversation export.

#### Full Project Context

```bash
bash claude-memory/bin/cc-memspan --project mindjot
```

Loads project context from `memory/projects/<project>/`:
- **`context.md`** - **Primary context** (lightweight, ~2-5KB) - **Recommended for most sessions**
- **`conversations.json`** - Full conversation history (optional, load ad-hoc when needed)

**Setting up project files:**

1. **Generate context.md (Recommended)**:
   - Export project conversations using `export-chatgpt-conversations`
   - Use the prompt in `export-chatgpt-conversations/generate-context-prompt.md` with Claude to generate `context.md`
   - Or create manually with project overview, architecture, goals, and current state
   - Save to `memory/projects/<project>/context.md`
   - **Note:** Future release will automate this process

2. **Export conversations.json (Optional)**:
   - Use `export-chatgpt-conversations` to export a project
   - Copy to `memory/projects/<project>/conversations.json`
   - **Use sparingly** - only when you need to reference specific historical conversations

**Usage pattern:**
- **Most sessions**: Load `context.md` only (lightweight, current state)
- **Deep historical work**: Load `conversations.json` ad-hoc when needed
- **Note:** Loading `conversations.json` significantly increases token usage

#### Identity Only

```bash
bash claude-memory/bin/cc-memspan --identity
```

Loads just your identity—useful for quick questions where memories aren't needed.

#### Control File Only

```bash
bash claude-memory/bin/cc-memspan
```

Loads only `CLAUDE.md` (data-free control file with instructions). Minimal context.

#### Using Current Project

```bash
# Set current project
echo mindjot > claude-memory/memory/current-project

# Use it
bash claude-memory/bin/cc-memspan --use-current --identity
```

#### Passing Arguments to Claude

Use `--` to pass extra arguments to the `claude` command:

```bash
bash claude-memory/bin/cc-memspan --identity -- "help me refactor this code"
```

#### Dry Run

See what command would be executed:

```bash
bash claude-memory/bin/cc-memspan --identity --memories --dry-run
```

### How It Works

1. **Reads Context Files**: The script reads selected context files (identity, memories, projects)
2. **Combines into System Prompt**: Files are combined into a system prompt block
3. **Launches Claude**: Runs `claude` with `--append-system-prompt`

This means the context is sent with every message, so Claude has access to your identity and memories throughout the session.

### CLAUDE.md Instructions

`CLAUDE.md` is a **data-free control file** that provides instructions to Claude:

- **Where context files live** - Points to identity, memories, and project files
- **Memory precedence rules** - Claude memories > ChatGPT memories > identity
- **Memory saving behavior** - How Claude should save new memories during sessions
- **Historical data loading** - Instructions to ask before loading conversation history

**Key behaviors:**
- Claude does **not** assume identity or memories unless files are explicitly loaded via `cc-memspan`
- If asked about prior decisions/history without context, Claude will ask whether to load specific files
- Historical conversations are loaded **ad-hoc** when needed (not automatically)

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

**Example Files:**
- See `claude-memory/memory/claude/index-example.json` for the complete index structure with config and entry metadata
- See the `claude-memory/memory/claude/entries/` directory for example entry files showing the markdown format
- See `claude-memory/memory/claude/README.md` for full documentation on the memory system

### How This Differs from Claude's Default Memory

**Claude's Built-in Memory:**
- Managed by Anthropic, stored on their servers
- Automatic and opaque (you don't see what's stored)
- Platform-locked to Claude/Anthropic
- Not portable to other LLMs or systems

**Memspan's File-Based Memory:**
- **You control everything** - files on your system
- **Transparent** - you can see and edit all memories
- **Portable** - standard formats work with any LLM
- **Selective** - you choose what to load per session
- **Independent** - doesn't interfere with Claude's built-in memory

**Advantages:**
- **Portability**: Your data works with GPT-4, local models, or future LLMs
- **Control**: See, edit, and version-control your memories
- **Ownership**: Files on your system, not locked to a vendor
- **Future-proof**: Foundation for digital twins or custom AI agents

### File Resolution

The script looks for files in this order:

**Identity:**
1. `memory/identity/core-identity.md` (if present)
2. `memory/identity/core-identity.json` (primary format from export)
3. `../identity-archive/core-identity.json` (fallback)

**Memories:**
- `memory/chatgpt/memories_export.md`

**Projects:**
- `memory/projects/<project>/context.md`
- `memory/projects/<project>/conversations.json`

**Projects Index:**
- `memory/projects/projects.json`

Missing files are warned about but skipped (the script continues).

---

## Creating Aliases

To avoid typing the full path every time, create shell aliases. Here are examples for macOS/Linux using `~/.bash_profile` or `~/.zshrc`:

### Basic Alias

```bash
# Add to ~/.bash_profile or ~/.zshrc
alias cc-memspan='bash ~/path/to/memspan/claude-memory/bin/cc-memspan'
```

Now you can use:
```bash
cc-memspan --identity
```

### Convenience Aliases

Create shortcuts for common patterns:

```bash
# Add to ~/.bash_profile or ~/.zshrc

# Base alias
alias cc-memspan='bash ~/path/to/memspan/claude-memory/bin/cc-memspan'

# Claude CLI shortcut
alias cc='claude'

# Common patterns
alias cc-me='cc-memspan --identity --memories'
alias cc-project='cc-memspan --identity --memories --projects-index'
```

### Usage with Aliases

```bash
# Load identity and memories
cc-me

# Load identity, memories, and projects index (lightweight project awareness)
cc-project

# Load full context for a project (ad-hoc, higher token usage)
cc-memspan --project mindjot

# Just identity
cc-memspan --identity
```

### Applying Changes

After adding aliases, reload your shell configuration:

```bash
# For bash
source ~/.bash_profile

# For zsh
source ~/.zshrc
```

Or open a new terminal window.

### Example: Complete Setup

Here's a complete example for `~/.bash_profile`:

```bash
# Memspan aliases
alias cc-memspan='bash ~/path/to/memspan/claude-memory/bin/cc-memspan'
alias cc='claude'
alias cc-me='cc-memspan --identity --memories'
alias cc-project='cc-memspan --identity --memories --projects-index'
```

### Customizing the Path

If your Memspan directory is in a different location, adjust the path:

```bash
# Example: if memspan is in ~/Projects/memspan
alias cc-memspan='bash ~/Projects/memspan/claude-memory/bin/cc-memspan'
```

### Environment Variables

You can also set `CLAUDE_CMD` if your Claude CLI has a different name:

```bash
# In ~/.bash_profile or ~/.zshrc
export CLAUDE_CMD="claude"  # or whatever your CLI is named
```

---

## Next Steps

1. **Extract Your Identity**: Follow the [Identity Extraction](#extracting-identity) steps
2. **Set Up Aliases**: Create convenient aliases for `cc-memspan`
3. **Try It Out**: Run `cc-memspan --identity` and start a conversation
4. **Extract Memories**: See `export-chatgpt-memories/README.md` for memory export
5. **Export Conversations**: See `export-chatgpt-conversations/README.md` for conversation export and project correlation

## Additional Resources

- **[Main README](README.md)**: Complete project overview
- **[Main README](../README.md)**: Complete project overview and architecture
- **[Claude Memory README](claude-memory/README.md)**: Detailed usage guide
- **[Identity Archive README](identity-archive/README.md)**: Identity extraction details
- **[ChatGPT Memories README](export-chatgpt-memories/README.md)**: Memory export guide
- **[Conversation Export README](export-chatgpt-conversations/README.md)**: Conversation export and project correlation guide

---

## Troubleshooting

### Claude CLI Not Found

```bash
# Check if claude is installed
which claude

# If not, install Claude Code CLI (see Claude documentation)
```

### Identity File Not Found

```bash
# Check if identity file exists
ls -la claude-memory/memory/identity/

# If missing, extract identity first (see Extracting Identity section)
```

### Script Permission Denied

```bash
# Make script executable
chmod +x claude-memory/bin/cc-memspan
```

### Alias Not Working

```bash
# Reload shell configuration
source ~/.bash_profile  # or ~/.zshrc

# Or check alias is defined
alias cc-memspan
```

---

## Summary

Memspan gives you:

✅ **Portable Memory**: Extract identity, memories, and conversations from ChatGPT  
✅ **Selective Loading**: Choose what context to load per session  
✅ **File-Based**: No databases, just files you control  
✅ **Tool-Agnostic**: Works with any LLM interface  

Start by extracting your identity, then use `cc-memspan` to load it into Claude Code sessions. Create aliases for convenience, and gradually add memories and project context as needed.

