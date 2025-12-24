# ChatGPT Projects & Conversations Export Tools

A set of Python tools to export and correlate ChatGPT Projects with their conversation history.

## Why This Tool Exists

**The Problem:** ChatGPT's official data export does not include project information. When you export your conversation history, you get a flat list of conversations with no way to know which project (if any) each conversation belongs to.

This creates several challenges:

- **Data Portability**: You can't easily migrate your organized project structure to another platform
- **Historical Analysis**: It's difficult to analyze conversations by project context
- **Data Ownership**: Without project metadata, you lose the organizational structure you've built
- **Migration**: Moving to other GPT platforms (Claude, local models, etc.) requires manual correlation of conversations to projects

**The Solution:** This toolkit bridges the gap by:

1. Extracting project metadata from ChatGPT's API (which isn't included in the standard export)
2. Correlating conversations with their projects using the `gizmo_id` field
3. Providing a unified export format that preserves your project organization

## Overview

ChatGPT Projects (internally called "snorlax gizmos") organize conversations into folders with shared context and memory. This toolkit provides:

1. **Project Export Script** - Extracts project metadata from the ChatGPT API
2. **Project Conversations Script** - Correlates projects with your exported conversation history

High-level data relationship:

```text
Account
 └── Project (gizmo / snorlax)
       └── Conversations
```

**What You Get:**

- Complete project-to-conversation mappings
- Project metadata (names, creation dates, memory settings)
- Categorized exports (project conversations, regular conversations, orphaned projects)
- Full message content export (optional)

---

## Prerequisites

### Python

Python 3.6+ is required. No additional dependencies needed.

---

## Step 1: Export Your ChatGPT Data

ChatGPT allows you to export all your data as a zip file.

1. Go to **Settings → Data Controls → Export Data** in ChatGPT
2. Request your data export
3. You'll receive an email with a download link
4. Download and extract the zip file

The zip file contains several files, but the key one for this tool is:

- **`conversations.json`** - Your complete conversation history

Extract this file to: `conversations.json`

---

## Step 2: Export Your Projects List

**Important:** The ChatGPT data export does **not** include project metadata. This is a significant limitation of the official export—you get all your conversations, but no information about which projects they belong to.

To work around this limitation, we use the ChatGPT API to extract project information separately. The script replays the same API call the ChatGPT web UI uses to populate the sidebar.

### How It Works

The script replays the same API call the ChatGPT web UI uses to populate the sidebar:

```http
GET /backend-api/gizmos/snorlax/sidebar
```

### Authentication

The script reuses your browser credentials:

1. Open ChatGPT in your browser
2. Open DevTools → Network tab
3. Refresh the page or click on Projects in the sidebar
4. Find the request to `/gizmos/snorlax/sidebar`
5. Right-click → **Copy → Copy as cURL**
6. Paste into `export-chatgpt-conversations/curl.txt`

### Run the Export

```bash
cd export-chatgpt-conversations
python3 chatgpt_projects_dump.py --curl-file curl.txt
```

This creates:
- **`projects.json`** - Cleaned project metadata
- **`projects_raw.json`** - Full API responses (for debugging)

### Project Fields

| Field | Description |
|-------|-------------|
| `project_id` | Stable project identifier |
| `name` | Project name |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification |
| `num_interactions` | Number of chats |
| `memory_enabled` | Memory on/off |
| `memory_scope` | Global vs project-scoped |

---

## Step 3: Correlate Projects with Conversations

Now use the main script to link projects with their conversations via the `gizmo_id` field.

### Commands

```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py <command> [options]
```

| Command | Description |
|---------|-------------|
| `list-projects` | List all projects with conversation counts |
| `list <project>` | List conversations for a specific project |
| `export` | Export all project-conversation mappings to JSON |
| `export-project <project>` | Export a single project with full message content |
| `export-non-project` | Export all conversations that don't belong to any project |

### Global Options

```text
--projects-file PATH       Path to projects.json
                           (default: projects.json)

--conversations-file PATH  Path to conversations.json
                           (default: conversations.json)
```

---

## Usage Examples

### List All Projects

```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py list-projects
```

Output:

```text
Project Name                              Conversations Interactions
----------------------------------------------------------------------
My Research Project                                  53          307
Work - Client A                                      26           61
Personal Notes                                       22          143
----------------------------------------------------------------------
Total: 39 projects, 398 project conversations, 3067 non-project conversations
```

### List Conversations for a Project

By name or partial match:
```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py list "My Research Project"
python3 export-chatgpt-conversations/chatgpt_project_conversations.py list "Research"
```

By project ID:
```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py list g-p-676875c6bb248191aeb9391bf6fc7fb3
```

### List with Message Content

```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py list "Research" --with-messages
```

### Export All Projects

Metadata only:
```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export
```

With full messages (warning: large files):
```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export --with-messages
```

### Export a Single Project

```bash
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-project "My Research Project"
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-project "Research" -o research.json
```

**Use case:** Export project conversations to generate `context.md` or for ad-hoc loading in Claude sessions.

**Next steps:**
- Use `generate-context-prompt.md` with Claude to create a lightweight `context.md` from the exported conversations
- Copy the exported JSON to `memory/projects/<project>/conversations.json` if you need full conversation history

### Export Non-Project Conversations

Export all conversations that don't belong to any project (regular chats and custom GPT conversations):

```bash
# Metadata only
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-non-project

# With full message content
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-non-project --with-messages

# Custom output file
python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-non-project -o my_regular_chats.json
```

This creates a JSON file with:
- **Custom GPT conversations**: Conversations with custom GPTs (not projects)
- **Regular conversations**: Standard ChatGPT chats without any project or custom GPT

---

## Output Format

### Metadata Export

```json
{
  "generated_at": "2025-12-14T18:31:51.331179",
  "summary": {
    "total_projects": 39,
    "total_conversations": 3465,
    "project_conversations": 242,
    "non_project_conversations": 3067
  },
  "projects": [
    {
      "project_id": "g-p-...",
      "name": "My Research Project",
      "created_at": "2024-12-22T20:25:42.731126+00:00",
      "num_interactions": 307,
      "conversation_count": 53,
      "conversations": [...]
    }
  ],
  "non_project_conversations": {...},
  "orphaned_project_conversations": {...}
}
```

### With Messages

```json
{
  "conversations": [
    {
      "id": "69026a31-...",
      "title": "Topic Analysis Discussion",
      "messages": [
        {
          "role": "user",
          "content": "Can you help me analyze this?",
          "create_time": 1761765938.749404
        },
        {
          "role": "assistant",
          "content": "I'd be happy to help...",
          "model": "gpt-4o"
        }
      ]
    }
  ]
}
```

---

## Backend Endpoints & Data Structures

### ChatGPT API Endpoints

This toolkit interacts with ChatGPT's internal API endpoints:

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/backend-api/gizmos/snorlax/sidebar` | Retrieve projects list | GET |
| Data Export (via ChatGPT UI) | Download conversation history | Manual export |

**Note:** These are internal endpoints used by the ChatGPT web interface. They are not part of the official OpenAI API and may change without notice.

### Project IDs & Gizmo IDs

ChatGPT uses a "gizmo" system internally to organize content. Projects are a specific type of gizmo called "snorlax gizmos":

| ID Type | Format | Example | Description |
|---------|--------|---------|-------------|
| **Project ID** | `g-p-{hex}` | `g-p-691113bac1f48191b162d92962b703f1` | Unique identifier for a ChatGPT Project |
| **Custom GPT ID** | `g-{hex}` | `g-67a18e2e94b881919c8c2ed76adc9ce9` | Identifier for custom GPTs (not projects) |
| **Conversation ID** | UUID | `693f2bb6-a914-8330-a5a1-aef63dd12647` | Unique identifier for a conversation |

**Key Relationships:**

- A conversation's `gizmo_id` field links it to a project (when `gizmo_id` matches a project's `project_id`)
- Project IDs always start with `g-p-`
- Custom GPT gizmo IDs start with `g-` but not `g-p-`
- Regular conversations have `gizmo_id: null`

### Project Data Structure

From the API, each project contains:

```json
{
  "project_id": "g-p-691113bac1f48191b162d92962b703f1",
  "name": "Health Research",
  "short_url": "g-p-691113bac1f48191b162d92962b703f1-health-research",
  "created_at": "2024-12-22T20:25:42.731126+00:00",
  "updated_at": "2025-09-04T18:52:33.696935+00:00",
  "last_interacted_at": "2025-10-29T19:25:54.247571+00:00",
  "num_interactions": 307,
  "memory_enabled": true,
  "memory_scope": "global",
  "organization_id": "org-...",
  "author": "Eric BLUE"
}
```

### Conversation Data Structure

From the export, each conversation contains:

```json
{
  "id": "693f2bb6-a914-8330-a5a1-aef63dd12647",
  "title": "Claude code vector db setup",
  "gizmo_id": "g-p-691113bac1f48191b162d92962b703f1",
  "gizmo_type": null,
  "create_time": 1761765938.749404,
  "update_time": 1761765955.241624,
  "mapping": { ... },
  "default_model_slug": "gpt-4o",
  "is_archived": false,
  "memory_scope": "global"
}
```

**Important Fields:**

- `gizmo_id`: Links to project (matches `project_id` when part of a project)
- `gizmo_type`: `null` (regular/project), `"gpt"` (custom GPT)
- `mapping`: Tree structure containing all messages (see below)

### Message Mapping Structure

Conversations store messages in a tree structure called `mapping`. Each node represents a point in the conversation:

```json
{
  "mapping": {
    "node-id-1": {
      "id": "node-id-1",
      "parent": null,
      "children": ["node-id-2"],
      "message": {
        "id": "msg-123",
        "author": { "role": "user" },
        "content": {
          "parts": ["Hello, how are you?"]
        },
        "create_time": 1761765938.749404,
        "metadata": { "model_slug": "gpt-4o" }
      }
    },
    "node-id-2": {
      "id": "node-id-2",
      "parent": "node-id-1",
      "children": [],
      "message": { ... }
    }
  }
}
```

**Tree Structure Notes:**

- Root nodes have `parent: null`
- Messages are linked via `parent` → `children` relationships
- Linear conversations follow a single path through the tree
- Branching conversations (regeneration, edits) create multiple child paths
- The tool extracts messages by traversing the tree in chronological order

---

## Data Model & Relationships

### Hierarchy Overview

```text
Account
 └── Projects (snorlax gizmos)
       ├── Project Metadata (from API)
       │     ├── project_id: "g-p-..."
       │     ├── name, created_at, memory settings
       │     └── num_interactions
       │
       └── Conversations (from export)
             ├── conversation.id: UUID
             ├── gizmo_id: "g-p-..." (links to project)
             ├── title, timestamps
             └── mapping: { ... }
                   └── Message Nodes
                         ├── node.id
                         ├── parent/children (tree links)
                         └── message: { role, content, model }
```

### Linking Projects to Conversations

The correlation works by matching:

1. **Project → Conversation**: `project.project_id` === `conversation.gizmo_id`
2. **Conversation → Messages**: Traverse `conversation.mapping` tree structure

### Example Flow

```text
1. API Call: GET /backend-api/gizmos/snorlax/sidebar
   → Returns: List of projects with project_id = "g-p-abc123"

2. Export: conversations.json
   → Contains: Conversation with gizmo_id = "g-p-abc123"

3. Correlation:
   project.project_id ("g-p-abc123") 
   === 
   conversation.gizmo_id ("g-p-abc123")
   → Match! This conversation belongs to this project

4. Message Extraction:
   conversation.mapping → Tree traversal → Chronological messages
```

### Conversation Categories Explained

Based on the data structure:

| Category | `gizmo_id` | `gizmo_type` | Description |
|----------|------------|--------------|-------------|
| **Project conversations** | `g-p-...` | `null` | Linked to active project |
| **Custom GPT conversations** | `g-...` (not `g-p-`) | `"gpt"` | Used with custom GPTs |
| **Regular conversations** | `null` | `null` | Standard ChatGPT chats |
| **Orphaned project conversations** | `g-p-...` | `null` | Project deleted but conversation remains |

**Why Orphaned Conversations Exist:**

- You delete a project in ChatGPT
- The conversation history still references the old `gizmo_id`
- The project no longer appears in the API response
- The conversation is "orphaned" (project metadata lost)

---

## Conversation Categories

The tool categorizes conversations into:

| Category | Description |
|----------|-------------|
| **Project conversations** | Linked to an active project via `gizmo_id` |
| **Custom GPT conversations** | Used with custom GPTs (not projects) |
| **Regular conversations** | Standard ChatGPT chats without project/GPT |
| **Orphaned project conversations** | Linked to deleted projects |

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| No projects returned | Wrong JSON path or stale curl | Re-capture curl.txt |
| 401 errors | Expired cookies | Re-capture curl.txt from fresh session |
| Project not found | Typo in project name | Use `list-projects` to see names, or use project ID |
| Missing conversations | Old export | Request a new data export from ChatGPT |
| Large export files | Too much data | Use `export-project` for individual projects |

---

## Legal & Ethical Notes

- Access only your own data
- Do not share private API endpoints or credentials
- Do not scrape at scale
- Respect OpenAI terms of service
