.PHONY: help setup check status validate identity-prompt identity-check identity-validate memories-check projects-list memspan-identity memspan-identity-memories memspan-projects-index memspan-full memspan-check aliases-show aliases-install clean

# Variables
MEMSPAN_ROOT := $(shell pwd)
CLAUDE_MEMORY := $(MEMSPAN_ROOT)/claude-memory
MEMORY_ROOT := $(CLAUDE_MEMORY)/memory
IDENTITY_DIR := $(MEMORY_ROOT)/identity
MEMORIES_DIR := $(MEMORY_ROOT)/chatgpt
PROJECTS_DIR := $(MEMORY_ROOT)/projects
CC_MEMSPAN := $(CLAUDE_MEMORY)/bin/cc-memspan

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "Memspan Makefile - Common Tasks"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup                        # Create directory structure"
	@echo "  make check                        # Check prerequisites"
	@echo "  make status                       # Show status of all memory files"
	@echo "  make memspan-identity             # Launch Claude with identity"
	@echo "  make memspan-identity-memories    # Launch with identity + memories (recommended)"
	@echo "  make memspan-projects-index       # Launch with identity + memories + projects index"
	@echo "  make memspan-full PROJECT=mindjot  # Launch with full context"

setup: ## Create directory structure for memory files (idempotent)
	@if [ ! -d $(IDENTITY_DIR) ] || [ ! -d $(MEMORIES_DIR) ] || [ ! -d $(PROJECTS_DIR) ] || [ ! -d $(MEMORY_ROOT)/claude/entries ]; then \
		echo "$(GREEN)Setting up Memspan directory structure...$(NC)"; \
		mkdir -p $(IDENTITY_DIR); \
		mkdir -p $(MEMORIES_DIR); \
		mkdir -p $(PROJECTS_DIR); \
		mkdir -p $(MEMORY_ROOT)/claude/entries; \
		echo "$(GREEN)✓ Directory structure created$(NC)"; \
	else \
		echo "$(GREEN)✓ Directory structure already exists$(NC)"; \
	fi
	@echo ""
	@echo "Next steps:"
	@echo "  1. Extract identity: make identity-prompt"
	@echo "  2. Export memories: See export-chatgpt-memories/README.md"
	@echo "  3. Check status: make status"

check: ## Check prerequisites (claude CLI, Python, etc.)
	@echo "$(GREEN)Checking prerequisites...$(NC)"
	@echo ""
	@which claude > /dev/null 2>&1 && echo "$(GREEN)✓ Claude CLI found$(NC)" || echo "$(RED)✗ Claude CLI not found - install Claude Code CLI$(NC)"
	@which python3 > /dev/null 2>&1 && echo "$(GREEN)✓ Python 3 found$(NC)" || echo "$(RED)✗ Python 3 not found$(NC)"
	@test -f $(CC_MEMSPAN) && echo "$(GREEN)✓ cc-memspan script found$(NC)" || echo "$(RED)✗ cc-memspan script not found$(NC)"
	@test -f $(CLAUDE_MEMORY)/CLAUDE.md && echo "$(GREEN)✓ CLAUDE.md found$(NC)" || echo "$(YELLOW)⚠ CLAUDE.md not found$(NC)"
	@echo ""

status: ## Show status of all memory files
	@echo "$(GREEN)Memspan Memory Status$(NC)"
	@echo "=========================="
	@echo ""
	@echo "$(YELLOW)Identity:$(NC)"
	@test -f $(IDENTITY_DIR)/core-identity.json && echo "  $(GREEN)✓$(NC) core-identity.json" || echo "  $(RED)✗$(NC) core-identity.json (missing)"
	@test -f $(IDENTITY_DIR)/core-identity.md && echo "  $(GREEN)✓$(NC) core-identity.md" || echo "  $(YELLOW)○$(NC) core-identity.md (optional)"
	@echo ""
	@echo "$(YELLOW)Memories:$(NC)"
	@test -f $(MEMORIES_DIR)/memories_export.md && echo "  $(GREEN)✓$(NC) memories_export.md" || echo "  $(RED)✗$(NC) memories_export.md (missing)"
	@test -f $(MEMORIES_DIR)/memories.md && echo "  $(GREEN)✓$(NC) memories.md" || echo "  $(YELLOW)○$(NC) memories.md (optional)"
	@echo ""
	@echo "$(YELLOW)Projects:$(NC)"
	@test -f $(PROJECTS_DIR)/projects.json && echo "  $(GREEN)✓$(NC) projects.json" || echo "  $(YELLOW)○$(NC) projects.json (optional)"
	@if [ -d $(PROJECTS_DIR) ] && [ -n "$$(find $(PROJECTS_DIR) -mindepth 1 -maxdepth 1 -type d 2>/dev/null)" ]; then \
		echo "  Projects found:"; \
		for dir in $(PROJECTS_DIR)/*/; do \
			project=$$(basename $$dir); \
			if [ -d "$$dir" ] && [ "$$project" != "README.md" ]; then \
				echo "    - $$project"; \
			fi; \
		done; \
	else \
		echo "  $(YELLOW)○$(NC) No projects configured"; \
	fi
	@echo ""

validate: identity-check memories-check ## Validate all required files exist
	@echo "$(GREEN)Validation complete$(NC)"

identity-prompt: ## Show location of identity extraction prompt
	@echo "$(GREEN)Identity Extraction Prompt$(NC)"
	@echo "================================"
	@echo ""
	@echo "Location: $(MEMSPAN_ROOT)/identity-archive/identity-archive-prompt.md"
	@echo ""
	@test -f $(MEMSPAN_ROOT)/identity-archive/identity-archive-prompt.md && \
		echo "$(GREEN)✓ Prompt file found$(NC)" || \
		echo "$(RED)✗ Prompt file not found$(NC)"
	@echo ""
	@echo "Instructions:"
	@echo "  1. Open ChatGPT web interface (chat.openai.com)"
	@echo "  2. Ensure memory is enabled in Settings → Personalization & Memory"
	@echo "  3. Copy the prompt from the file above"
	@echo "  4. Paste into a new ChatGPT conversation"
	@echo "  5. Save the JSON output to: $(IDENTITY_DIR)/core-identity.json"
	@echo ""
	@echo "See identity-archive/README.md for detailed instructions."

identity-check: ## Check if identity file exists
	@if test -f $(IDENTITY_DIR)/core-identity.json || test -f $(IDENTITY_DIR)/core-identity.md; then \
		echo "$(GREEN)✓ Identity file found$(NC)"; \
		test -f $(IDENTITY_DIR)/core-identity.json && echo "  Location: $(IDENTITY_DIR)/core-identity.json" || true; \
		test -f $(IDENTITY_DIR)/core-identity.md && echo "  Location: $(IDENTITY_DIR)/core-identity.md" || true; \
	else \
		echo "$(RED)✗ Identity file not found$(NC)"; \
		echo "  Expected: $(IDENTITY_DIR)/core-identity.json or .md"; \
		echo "  Run: make identity-prompt"; \
		exit 1; \
	fi

identity-validate: identity-check ## Validate identity JSON format
	@if test -f $(IDENTITY_DIR)/core-identity.json; then \
		echo "$(GREEN)Validating identity JSON...$(NC)"; \
		python3 -m json.tool $(IDENTITY_DIR)/core-identity.json > /dev/null 2>&1 && \
			echo "$(GREEN)✓ Valid JSON$(NC)" || \
			(echo "$(RED)✗ Invalid JSON$(NC)" && exit 1); \
	else \
		echo "$(YELLOW)⚠ No JSON file to validate (checking .md instead)$(NC)"; \
	fi

memories-check: ## Check if memories file exists
	@if test -f $(MEMORIES_DIR)/memories_export.md; then \
		echo "$(GREEN)✓ Memories file found$(NC)"; \
		echo "  Location: $(MEMORIES_DIR)/memories_export.md"; \
	else \
		echo "$(YELLOW)⚠ Memories file not found (optional)$(NC)"; \
		echo "  Expected: $(MEMORIES_DIR)/memories_export.md"; \
		echo "  See export-chatgpt-memories/README.md for instructions"; \
	fi

projects-list: ## List available projects
	@echo "$(GREEN)Available Projects$(NC)"
	@echo "==================="
	@echo ""
	@if [ -d $(PROJECTS_DIR) ] && [ -n "$$(find $(PROJECTS_DIR) -mindepth 1 -maxdepth 1 -type d 2>/dev/null)" ]; then \
		for dir in $(PROJECTS_DIR)/*/; do \
			project=$$(basename $$dir); \
			if [ -d "$$dir" ] && [ "$$project" != "README.md" ]; then \
				echo "  - $$project"; \
				test -f $$dir/context.md && echo "    $(GREEN)✓$(NC) context.md" || echo "    $(YELLOW)○$(NC) context.md"; \
				test -f $$dir/decisions.json && echo "    $(GREEN)✓$(NC) decisions.json" || echo "    $(YELLOW)○$(NC) decisions.json"; \
				test -f $$dir/conversations.json && echo "    $(GREEN)✓$(NC) conversations.json" || echo "    $(YELLOW)○$(NC) conversations.json"; \
			fi; \
		done; \
	else \
		echo "$(YELLOW)No projects found$(NC)"; \
		echo "  Create project directories in: $(PROJECTS_DIR)/"; \
	fi
	@echo ""

memspan-identity: identity-check ## Launch Claude with identity context
	@echo "$(GREEN)Launching Claude with identity...$(NC)"
	@bash $(CC_MEMSPAN) --identity

memspan-identity-memories: identity-check ## Launch Claude with identity and memories (recommended starting point)
	@echo "$(GREEN)Launching Claude with identity and memories...$(NC)"
	@bash $(CC_MEMSPAN) --identity --memories

memspan-projects-index: identity-check ## Launch Claude with identity, memories, and projects index (lightweight project awareness)
	@echo "$(GREEN)Launching Claude with identity, memories, and projects index...$(NC)"
	@bash $(CC_MEMSPAN) --identity --memories --projects-index

memspan-full: identity-check ## Launch Claude with full context (requires PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(RED)Error: PROJECT not specified$(NC)"; \
		echo "Usage: make memspan-full PROJECT=project-name"; \
		echo ""; \
		echo "Available projects:"; \
		$(MAKE) projects-list; \
		exit 1; \
	fi
	@echo "$(GREEN)Launching Claude with full context for project: $(PROJECT)$(NC)"
	@bash $(CC_MEMSPAN) --full $(PROJECT)

memspan-check: ## Check what context files would be loaded
	@echo "$(GREEN)Memspan Context File Check$(NC)"
	@echo "=============================="
	@echo ""
	@echo "Files that would be loaded:"
	@bash $(CC_MEMSPAN) --identity --memories --dry-run 2>&1 | grep -E "(WARN|Context)" || true
	@echo ""
	@echo "Run with --dry-run to see full command:"
	@echo "  bash $(CC_MEMSPAN) --identity --memories --dry-run"

aliases-show: ## Show example shell aliases
	@echo "$(GREEN)Example Shell Aliases$(NC)"
	@echo "======================"
	@echo ""
	@echo "Add to ~/.bash_profile or ~/.zshrc:"
	@echo ""
	@echo "# Memspan aliases"
	@echo "alias cc-memspan='bash $(MEMSPAN_ROOT)/claude-memory/bin/cc-memspan'"
	@echo "alias cc='claude'"
	@echo "alias cc-me='cc-memspan --identity --memories'"
	@echo "alias cc-project='cc-memspan --identity --memories --projects-index'"
	@echo ""
	@echo "Then reload: source ~/.bash_profile  # or ~/.zshrc"

aliases-install: ## Help install aliases (interactive)
	@echo "$(GREEN)Installing Memspan Aliases$(NC)"
	@echo "============================"
	@echo ""
	@read -p "Which shell config file? (~/.bash_profile or ~/.zshrc) [~/.bash_profile]: " config_file; \
	config_file=$${config_file:-~/.bash_profile}; \
	if [ ! -f $$config_file ]; then \
		echo "Creating $$config_file..."; \
		touch $$config_file; \
	fi; \
	if grep -q "Memspan aliases" $$config_file; then \
		echo "$(YELLOW)Aliases already exist in $$config_file$(NC)"; \
	else \
		echo "" >> $$config_file; \
		echo "# Memspan aliases" >> $$config_file; \
		echo "alias cc-memspan='bash $(MEMSPAN_ROOT)/claude-memory/bin/cc-memspan'" >> $$config_file; \
		echo "alias cc='claude'" >> $$config_file; \
		echo "alias cc-me='cc-memspan --identity --memories'" >> $$config_file; \
		echo "alias cc-project='cc-memspan --identity --memories --projects-index'" >> $$config_file; \
		echo "$(GREEN)✓ Aliases added to $$config_file$(NC)"; \
		echo ""; \
		echo "Reload with: source $$config_file"; \
	fi

clean: ## Clean up temporary files (be careful!)
	@echo "$(YELLOW)Warning: This will not delete your memory files$(NC)"
	@echo "This target is reserved for future cleanup tasks."
	@echo "Your identity, memories, and projects are safe."

