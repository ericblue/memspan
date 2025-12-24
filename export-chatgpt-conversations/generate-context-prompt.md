# Generate Project Context.md from Conversations

Use this prompt with Claude to generate a `context.md` file from exported project conversations.

## Usage

1. Export your project conversations:
   ```bash
   python3 export-chatgpt-conversations/chatgpt_project_conversations.py export-project "Project Name" -o temp.json
   ```

2. Load the exported conversations and use this prompt with Claude:

---

## Prompt

I have exported ChatGPT conversations for my project. Please analyze the conversations and create a `context.md` file that provides a concise, current-state overview.

**Requirements:**
- Keep it concise (2-5KB total)
- Focus on **current state**, not historical details
- Extract key information that would be useful for future sessions

**Include these sections:**

1. **Project Overview**
   - Purpose and goals
   - Current status
   - Key stakeholders or context

2. **Architecture & Design**
   - Current system architecture
   - Technology stack
   - Key design decisions
   - Important patterns or conventions

3. **Active Goals & Priorities**
   - Current objectives
   - In-progress work
   - Upcoming priorities

4. **Key Decisions**
   - Important architectural decisions
   - Technology choices and rationale
   - Process or workflow decisions

5. **Current State**
   - What's working well
   - Current blockers or challenges
   - Recent changes or updates

6. **Next Steps**
   - Immediate next actions
   - Short-term roadmap items

**Format:**
- Use clear markdown headings
- Be specific and actionable
- Focus on information that would help someone (or an AI assistant) understand the project quickly
- Avoid duplicating information that's already clear from conversation history

Please generate the `context.md` content now.

---

## Future Automation

**Note:** This process will be automated in a future release. A script will:
- Export project conversations
- Automatically generate `context.md` using Claude Code
- Save it to the correct location in `memory/projects/<project>/context.md`

For now, use this prompt manually with Claude.

