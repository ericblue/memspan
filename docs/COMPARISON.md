# Memspan vs Other Memory Frameworks: Technical Comparison

Technical comparison of memspan.ai with other memory frameworks. Focus: architectural tradeoffs and use cases.

---

## Overview

**Memspan** is a file-first memory archive for **personal identity continuity and long-term context portability** across AI tools. Unlike frameworks built for agents and applications, memspan prioritizes:

- **Identity preservation** over isolated fact recall
- **File-first, user-owned** storage (Markdown/JSON)
- **Tool-agnostic design** (works with any LLM interface)
- **Explicit control** (no silent summarization or automatic injection)

Most AI memory systems (Letta, Mem0, BasicMemory) are optimized for **agents and applications**—they rely on infrastructure, embeddings, and retrieval layers. Memspan solves a different problem: **personal identity and long-term context portability across AI tools**.

---

## File-First, Not File-Only

**Memspan is file-first, not file-only.** The filesystem is the source of truth, but the architecture supports optional enhancements:

### Current: Filesystem-Only (Default)
- Pure file system: `memory/identity/`, `memory/claude/`, `memory/projects/`
- No database dependencies
- Human-readable formats (Markdown, JSON)
- Version control friendly (git-trackable)
- Portable across machines via file copy

### Future: Optional Enhancements (Planned)
- **MCP Server**: On-demand memory access via Model Context Protocol
- **Database Index**: Optional SQLite/Postgres index for fast search (files remain source of truth)
- **Knowledge Graph**: Optional relationship graph (Graphiti, Memgraph, FalkorDB adapters)
- **Vector Search**: Optional embeddings (LanceDB/ChromaDB) for semantic search

**Architecture Pattern:**
```
Filesystem (Source of Truth)
    ↓ (optional sync)
Database Index (Derived, can be rebuilt)
    ↓
MCP Server (Uses adapter interface)
    ↓
Storage Adapters (FilesystemAdapter, GraphitiAdapter, etc.)
```

**Key Design Principles:**
1. **Files remain source of truth** - Database/graph are derived indexes
2. **Adapter pattern** - Pluggable backends (filesystem, Graphiti, Memgraph, etc.)
3. **Progressive enhancement** - Start simple, add complexity when needed
4. **No lock-in** - Can delete database/graph and revert to filesystem-only
5. **Backward compatible** - Existing workflows unchanged

See `docs/internal/ARCHITECTURE_TRANSITION.md` for detailed architecture plans.

---

## Core Architectural Differences

### Storage Layer

| Framework | Storage | Format | Infrastructure Required |
|-----------|---------|--------|------------------------|
| **Memspan** | File system (default) | Markdown + JSON | None (optional: DB/graph) |
| **Letta/MemGPT** | Database + services | Structured records | Database server |
| **Mem0** | Database + vectors | Embeddings + metadata | Database + vector store |
| **BasicMemory** | Files + database | Markdown + SQLite/Postgres | Database (SQLite minimal) |

**Tradeoff:** Filesystem-only = transparency and portability, but no built-in query engine. Optional enhancements add search/graph capabilities when needed.

### Access Pattern

| Framework | Access Method | Token Efficiency | On-Demand Retrieval |
|-----------|---------------|------------------|---------------------|
| **Memspan** | System prompt injection | Lower (loads upfront) | Planned: MCP |
| **Letta/MemGPT** | Agent memory API | Higher (selective) | Yes |
| **Mem0** | SDK/API calls | Higher (selective) | Yes |
| **BasicMemory** | MCP server tools | Higher (selective) | Yes |

**Current (filesystem-only):**
```bash
cc-memspan --identity --memories --project mindjot
# → Reads files → Combines → --append-system-prompt
```

**Future (MCP + adapter):**
- On-demand retrieval via MCP tools (`get_identity`, `search_memories`)
- Works with any adapter (FilesystemAdapter, GraphitiAdapter, etc.)

### Integration Model

| Framework | Integration | Protocol | Setup Complexity |
|-----------|-------------|----------|------------------|
| **Memspan** | Wrapper script (MCP planned) | CLI flags | Low (file-based) |
| **Letta/MemGPT** | Agent framework | Python SDK | Medium |
| **Mem0** | SDK/API | REST/GraphQL | Medium |
| **BasicMemory** | MCP server | Model Context Protocol | Medium |

**Current:** Bash wrapper (`cc-memspan`) - no server, works immediately  
**Future:** MCP server via adapter interface - optional, backward compatible

---

## Framework Comparisons

### Memspan vs Letta/MemGPT

| Aspect | Memspan | Letta/MemGPT |
|--------|---------|--------------|
| **Target** | People (personal continuity) | Agents (application memory) |
| **Storage** | Files (default) | Database + services |
| **Infrastructure** | None (optional) | Required |
| **Use Case** | Personal identity across tools | Agent state management |

**Choose Memspan:** Personal identity continuity, file-first, zero infrastructure  
**Choose Letta:** Building AI agents, need automatic summarization, agent frameworks

### Memspan vs Mem0

| Aspect | Memspan | Mem0 |
|--------|---------|------|
| **Target** | People (identity continuity) | Apps & agents (memory layer) |
| **Storage** | Files (default) | Database + vectors |
| **Extraction** | Manual | Automatic |
| **Control** | Explicit | Automatic |

**Choose Memspan:** Explicit control, manual curation, portability  
**Choose Mem0:** Automatic extraction, vector search, multi-user systems

### Memspan vs BasicMemory

| Aspect | Memspan | BasicMemory |
|--------|---------|-------------|
| **Target** | People (identity continuity) | Knowledge workers (PKM) |
| **Storage** | Files (default) | Files + database |
| **Graph** | Planned (optional) | Yes (current) |
| **MCP** | Planned (optional) | Yes (current) |
| **Focus** | Identity + memories | Knowledge graph |

**Choose Memspan:** Identity continuity, file-first, maximum portability  
**Choose BasicMemory:** Knowledge graphs, semantic search, MCP now

---

## Memspan Architecture

### Three-Tier Memory Model

1. **Core Identity**: Always-available personal context
   - `memory/identity/core-identity.json`

2. **Project/Framework Memory**: Session-selectable
   - `memory/projects/<project>/context.md`

3. **Historical Archive**: Indexed, retrieved on-demand
   - `memory/chatgpt/memories_export.md` (static)
   - `memory/claude/entries/*.md` (active)

### Current Access (Filesystem-Only)

```bash
cc-memspan --identity --memories --project mindjot
# → Reads files → Combines → --append-system-prompt
```

### Future Access (MCP + Adapter)

```typescript
// MCP tools via adapter interface:
- get_identity(): Returns condensed identity
- search_memories(query): Returns relevant memories (filtered)
- search_history(query): Keyword/semantic search
- get_conversation(id): Fetch specific chunks
```

**Benefit:** On-demand loading (only what's needed per tool call)

### Memory Precedence

1. Claude memories > ChatGPT memories
2. Newer entries > Older entries
3. Explicit corrections > Inferred information
4. Project context > Global memories > Identity

---

## Use Cases

### When Memspan Is the Right Fit

- Personal identity continuity across multiple LLM tools
- File-first philosophy (see/edit all memories directly)
- Tool portability (works with any LLM interface)
- Explicit control (decide what loads per session)
- Zero infrastructure (works immediately, no setup)

### When Other Frameworks Are Better

- **Letta/MemGPT:** Building AI agents, need automatic summarization
- **Mem0:** Building applications, need automatic extraction, vector search
- **BasicMemory:** Need knowledge graphs, semantic search, MCP now

---

## Feature Comparison

| Feature | Memspan | Letta | Mem0 | BasicMemory |
|---------|---------|-------|------|-------------|
| **Built for** | People | Agents | Apps & agents | Knowledge workers |
| **Storage** | Files (default) | Database | Database + vectors | Files + database |
| **Infrastructure** | None (optional) | Required | Required | SQLite minimal |
| **Portability** | High | Medium | Medium | Medium |
| **Identity Focus** | ✅ Primary | ❌ | ❌ | ❌ |
| **Vector Search** | Planned (optional) | ✅ | ✅ | ✅ |
| **MCP Integration** | Planned (optional) | ❌ | ❌ | ✅ |
| **Knowledge Graph** | Planned (optional) | ❌ | ❌ | ✅ |
| **Search** | Planned (optional) | ✅ | ✅ | ✅ |
| **Auto Extraction** | ❌ | ✅ | ✅ | ❌ |
| **Explicit Control** | ✅ | Partial | Partial | ✅ |
| **Zero Setup** | ✅ | ❌ | ❌ | Partial |

---

## Portability

**File-based advantages:**
- Cross-platform (works on any OS)
- Version control (git-trackable)
- Simple backup (file copy)
- Human-readable (edit with any text editor)
- Long-term (files survive technology changes)

**Migration:** Export from ChatGPT/Claude/other frameworks → convert to memspan format → copy directory

---

## Future Enhancements (Optional)

**Planned:**
- **MCP Server:** On-demand memory access via adapter interface
- **Database Index:** Optional SQLite/Postgres for fast search (files remain source of truth)
- **Knowledge Graph:** Optional relationship graph (Graphiti, Memgraph, FalkorDB adapters)
- **Vector Search:** Optional embeddings (LanceDB/ChromaDB) for semantic search

**Key Principle:** Files remain the source of truth. All enhancements are optional layers via adapter pattern. See `docs/internal/ARCHITECTURE_TRANSITION.md` for details.

---

## Conclusion

**Memspan is different because:**

1. **Built for people, not agents** - Personal identity continuity across tools
2. **File-first, not file-only** - Files are source of truth, optional enhancements available
3. **Tool-agnostic** - Works with any LLM interface
4. **Explicit control** - You decide what context loads
5. **Zero infrastructure** - Works immediately (optional enhancements when needed)

**These approaches are complementary:**

- **Memspan:** Personal identity, cross-tool continuity, file-first
- **Letta/MemGPT:** Agent memory management
- **Mem0:** Application-level memory extraction
- **BasicMemory:** Knowledge graph and PKM systems

**Value proposition:** The memory you carry with you, across tools, across time, under your control—starting simple, scaling when needed.

---

## References

- **Memspan:** [https://memspan.ai](https://memspan.ai) | [GitHub](https://github.com/ericblue/memspan)
- **Letta/MemGPT:** [https://github.com/letta-ai/letta](https://github.com/letta-ai/letta)
- **Mem0:** [https://github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)
- **BasicMemory:** [https://github.com/basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory)

---

*Last updated: 2025-12-15*

