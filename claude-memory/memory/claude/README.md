# Claude Memory System

This directory contains memories, observations, and insights captured during Claude sessions. It serves as Claude's evolving knowledge store about the user, complementing (and taking precedence over) the static ChatGPT memory export.

## Structure

```
memory/claude/
├── README.md          # This file
├── index.json         # Catalog of all entries with metadata
├── index-example.json # Example structure reference
└── entries/           # Individual memory files
    └── YYYY-MM-DD-slug.md
```

## How It Works

### Entry Types

Memories are categorized by `type` in the index:

| Type | Description |
|------|-------------|
| `fact` | Biographical info, preferences, things that are true |
| `insight` | Patterns, self-observations, reflections |
| `context` | Situational info that may change (projects, goals) |
| `correction` | Updates that supersede previous information |
| `preference` | Communication style, tool choices, how things should be done |

### Metadata Schema (index.json)

The `index.json` file has two main sections: `config` and `entries`.

**Full Structure:**

```json
{
  "config": {
    "notification_mode": "ask-first",
    "notification_modes_available": ["ask-first", "save-and-notify", "silent"],
    "notes": "Optional notes about the configuration"
  },
  "entries": [
    {
      "id": "2025-12-15-example-memory",
      "file": "entries/2025-12-15-example-memory.md",
      "created": "2025-12-15",
      "type": "insight",
      "topics": ["topic1", "topic2"],
      "summary": "One-line summary of the memory",
      "source": "conversation",
      "supersedes": null
    }
  ]
}
```

**Config Section:**
- `notification_mode`: Current mode for memory saving behavior (`ask-first`, `save-and-notify`, or `silent`)
- `notification_modes_available`: List of available modes
- `notes`: Optional notes about the configuration or system state

**Entry Fields:**
- `id`: Unique identifier (date + slug)
- `file`: Path to the entry file relative to `memory/claude/`
- `created`: Date created (YYYY-MM-DD)
- `type`: One of the entry types above (`fact`, `insight`, `context`, `correction`, `preference`)
- `topics`: Array of topic tags for filtering
- `summary`: Brief description for quick scanning
- `source`: Where this came from (`conversation`, `explicit-request`, `migration`)
- `supersedes`: ID of a previous entry this replaces (if applicable), or `null`

See `index-example.json` for a complete example with multiple entry types.

## Memory Behavior

### Notification Mode

Claude's memory saving behavior is configurable:

| Mode | Behavior |
|------|----------|
| `ask-first` | Claude asks before saving (current setting) |
| `save-and-notify` | Claude saves and mentions it (planned option) |
| `silent` | Claude saves without mention (planned option) |

**Current mode: `ask-first`**

> Future enhancement: Enable `save-and-notify` or `silent` modes once the system is tested and trusted.

### Precedence Rules

When information conflicts:
1. **Claude memories** take precedence over ChatGPT memories
2. **Newer entries** take precedence over older entries
3. **Explicit corrections** take precedence over inferred information

### What Gets Saved

Claude will proactively suggest saving:
- New biographical facts or corrections to existing ones
- Stated preferences or changes to preferences
- Significant insights or self-observations
- Goal updates or life context changes
- Decisions or commitments made during conversation

### Example: Proactive Memory Saving in Action

Here's how Claude proactively suggests saving a goal during a conversation:

```
> I have a goal to lose 10 pounds next year

⏺ Good goal! That's a reasonable and achievable target - roughly 0.8-1 lb per month 
allows for sustainable progress without extreme measures.

Looking at your current profile, you already have a solid foundation with strength 
training 3x/week and cardio 2x/week. Weight loss would mainly come down to nutrition 
adjustments alongside your existing routine.

---
Would you like me to save this goal to your memories (memory/claude/)? Per your 
current settings, I'm in ask-first mode for memory saves.
```

When you confirm, Claude will:
1. Create a new entry file in `entries/` (e.g., `2025-12-15-weight-loss-goal.md`)
2. Add the entry to `index.json` with appropriate metadata (type: `context`, topics: `["goals", "health"]`)
3. The memory will be available in future sessions when you load Claude memories

This demonstrates the **ask-first** mode: Claude recognizes the goal as memory-worthy and asks permission before saving.

## Usage

### Loading Context

To give Claude access to these memories, include in your context:
- `memory/claude/index.json` (for quick reference)
- Specific `entries/*.md` files as needed

### Manual Review

- Browse `entries/` to see all memories
- Check `index.json` to filter by type or topic
- Delete entries by removing the file and its index entry

### Example Files

- `index-example.json` - Complete example of the index structure with config and multiple entry types
- See the `entries/` directory for example entry files showing the markdown format

## Relationship to ChatGPT Memories

The `memory/chatgpt/` directory contains a static export from ChatGPT. It serves as historical reference but is not actively maintained. When ChatGPT memories need updating, the corrected version is saved here in `memory/claude/` with `supersedes` noted if applicable.

To re-sync with ChatGPT, re-export and replace `memory/chatgpt/memories_export.md`.
