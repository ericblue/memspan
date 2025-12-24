#!/usr/bin/env python3
"""
ChatGPT Project Conversations Tool

Correlates ChatGPT projects with their conversations from exported data.

Usage:
  # List conversations for a specific project (by name or ID)
  python3 chatgpt_project_conversations.py list "Health Research"
  python3 chatgpt_project_conversations.py list g-p-676875c6bb248191aeb9391bf6fc7fb3

  # List conversations with full message content
  python3 chatgpt_project_conversations.py list "Health Research" --with-messages

  # List all projects
  python3 chatgpt_project_conversations.py list-projects

  # Generate project_conversations.json with all mappings
  python3 chatgpt_project_conversations.py export

  # Export with full message content (large file!)
  python3 chatgpt_project_conversations.py export --with-messages

  # Export a single project with full messages
  python3 chatgpt_project_conversations.py export-project "Health Research"
  python3 chatgpt_project_conversations.py export-project "Health Research" -o health.json

  # Export all non-project conversations
  python3 chatgpt_project_conversations.py export-non-project
  python3 chatgpt_project_conversations.py export-non-project --with-messages -o all_non_project.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_projects(projects_path: str) -> list:
    """Load projects from projects.json"""
    with open(projects_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_conversations(conversations_path: str) -> list:
    """Load conversations from conversations.json"""
    with open(conversations_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_project_lookup(projects: list) -> dict:
    """Build lookup dicts for projects by ID and name"""
    by_id = {}
    by_name = {}
    for p in projects:
        pid = p.get('project_id')
        name = p.get('name', '').lower()
        if pid:
            by_id[pid] = p
        if name:
            by_name[name] = p
    return by_id, by_name


def group_conversations_by_project(conversations: list) -> dict:
    """Group conversations by their gizmo_id (project_id)"""
    grouped = defaultdict(list)
    for conv in conversations:
        gizmo_id = conv.get('gizmo_id')
        # Use None key for non-project conversations
        grouped[gizmo_id].append(conv)
    return grouped


def format_timestamp(ts) -> str:
    """Format a timestamp for display"""
    if ts is None:
        return "N/A"
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        return str(ts)[:19]
    except:
        return str(ts)[:19] if ts else "N/A"


def format_date(ts) -> str:
    """Format a timestamp as date only (YYYY-MM-DD)"""
    if ts is None:
        return "N/A"
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        # Try to parse ISO format string
        return str(ts)[:10]
    except:
        return str(ts)[:10] if ts else "N/A"


def get_message_count(conv: dict) -> int:
    """Get count of messages/nodes in a conversation"""
    mapping = conv.get('mapping', {})
    return len(mapping) if mapping else 0


def extract_messages_from_mapping(mapping: dict) -> list:
    """
    Extract messages from conversation mapping in chronological order.

    The mapping is a tree structure where each node has:
    - id: node ID
    - parent: parent node ID
    - children: list of child node IDs
    - message: the actual message content (may be None for root nodes)
    """
    if not mapping:
        return []

    messages = []

    # Build parent->children lookup and find root
    children_map = defaultdict(list)
    root_id = None

    for node_id, node in mapping.items():
        parent_id = node.get('parent')
        if parent_id is None:
            root_id = node_id
        else:
            children_map[parent_id].append(node_id)

    # Traverse tree in order (DFS following first child path for linear conversation)
    def traverse(node_id):
        if node_id not in mapping:
            return

        node = mapping[node_id]
        msg = node.get('message')

        if msg and msg.get('content'):
            content = msg.get('content', {})
            parts = content.get('parts', [])

            # Extract text content
            text_parts = []
            for part in parts:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict):
                    # Handle structured content (e.g., code blocks, images)
                    if 'text' in part:
                        text_parts.append(part['text'])

            text = '\n'.join(text_parts) if text_parts else ''

            if text.strip():  # Only include non-empty messages
                messages.append({
                    'id': msg.get('id'),
                    'role': (msg.get('author') or {}).get('role', 'unknown'),
                    'content': text,
                    'create_time': msg.get('create_time'),
                    'model': (msg.get('metadata') or {}).get('model_slug'),
                })

        # Follow children (for branching conversations, follow main path)
        children = children_map.get(node_id, [])
        for child_id in children:
            traverse(child_id)

    if root_id:
        traverse(root_id)

    return messages


def extract_conversation_summary(conv: dict, with_messages: bool = False) -> dict:
    """Extract summary of a conversation, optionally with full messages"""
    summary = {
        'id': conv.get('id'),
        'title': conv.get('title'),
        'create_time': conv.get('create_time'),
        'update_time': conv.get('update_time'),
        'message_count': get_message_count(conv),
        'model': conv.get('default_model_slug'),
        'is_archived': conv.get('is_archived', False),
        'memory_scope': conv.get('memory_scope'),
    }

    if with_messages:
        mapping = conv.get('mapping', {})
        summary['messages'] = extract_messages_from_mapping(mapping)

    return summary


def cmd_list_projects(projects: list, conversations_grouped: dict):
    """List all projects with conversation counts and date ranges"""
    print(f"{'Project Name':<35} {'Convs':>6} {'Interactions':>12} {'First':>12} {'Last':>12}")
    print("-" * 80)

    # Sort by conversation count descending
    project_data = []
    for p in projects:
        pid = p.get('project_id')
        convs = conversations_grouped.get(pid, [])
        conv_count = len(convs)
        
        # Find first and last conversation dates
        first_date = None
        last_date = None
        if convs:
            # First: earliest create_time (when first conversation started)
            # Last: latest update_time (when last conversation was updated)
            create_times = [c.get('create_time') for c in convs if c.get('create_time')]
            update_times = [c.get('update_time') for c in convs if c.get('update_time')]
            
            if create_times:
                first_date = min(create_times)
            if update_times:
                last_date = max(update_times)
        
        project_data.append((p, conv_count, first_date, last_date))

    project_data.sort(key=lambda x: x[1], reverse=True)

    for p, conv_count, first_date, last_date in project_data:
        name = p.get('name', '(unnamed)')[:33]
        interactions = p.get('num_interactions', 0)
        first_str = format_date(first_date) if first_date else "N/A"
        last_str = format_date(last_date) if last_date else "N/A"
        print(f"{name:<35} {conv_count:>6} {interactions:>12} {first_str:>12} {last_str:>12}")

    # Summary
    total_project_convs = sum(len(v) for k, v in conversations_grouped.items() if k is not None)
    non_project_convs = len(conversations_grouped.get(None, []))
    print("-" * 80)
    print(f"Total: {len(projects)} projects, {total_project_convs} project conversations, {non_project_convs} non-project conversations")


def find_project(project_query: str, projects: list):
    """Find a project by ID, name, or partial name match"""
    by_id, by_name = build_project_lookup(projects)

    # Find project by ID or name
    project = by_id.get(project_query) or by_name.get(project_query.lower())

    if not project:
        # Try partial name match
        for p in projects:
            if project_query.lower() in p.get('name', '').lower():
                project = p
                break

    return project


def cmd_list_conversations(project_query: str, projects: list, conversations_grouped: dict, with_messages: bool = False):
    """List conversations for a specific project"""
    project = find_project(project_query, projects)

    if not project:
        print(f"Error: Project '{project_query}' not found.", file=sys.stderr)
        print("\nAvailable projects:", file=sys.stderr)
        for p in projects[:10]:
            print(f"  - {p.get('name')} [{p.get('project_id')}]", file=sys.stderr)
        if len(projects) > 10:
            print(f"  ... and {len(projects) - 10} more", file=sys.stderr)
        sys.exit(1)

    pid = project.get('project_id')
    convs = conversations_grouped.get(pid, [])

    print(f"Project: {project.get('name')}")
    print(f"ID: {pid}")
    print(f"Created: {project.get('created_at', 'N/A')[:10]}")
    print(f"Interactions: {project.get('num_interactions', 0)}")
    print(f"Memory: {project.get('memory_scope', 'N/A')}")
    print()
    print(f"Conversations ({len(convs)}):")
    print("-" * 80)

    if not convs:
        print("  (no conversations found in export)")
        return

    # Sort by update time descending
    convs_sorted = sorted(convs, key=lambda c: c.get('update_time') or 0, reverse=True)

    for conv in convs_sorted:
        title = conv.get('title', '(untitled)')[:50]
        msg_count = get_message_count(conv)
        updated = format_timestamp(conv.get('update_time'))
        conv_id = conv.get('id', '')[:36]
        print(f"  {title:<50} {msg_count:>4} msgs  {updated}")
        print(f"    ID: {conv_id}")

        if with_messages:
            print()
            messages = extract_messages_from_mapping(conv.get('mapping', {}))
            for msg in messages:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                # Truncate long messages for display
                if len(content) > 500:
                    content = content[:500] + '... [truncated]'
                # Indent message content
                content_lines = content.split('\n')
                print(f"      [{role}]")
                for line in content_lines[:20]:  # Limit lines shown
                    print(f"        {line}")
                if len(content_lines) > 20:
                    print(f"        ... [{len(content_lines) - 20} more lines]")
                print()
            print("-" * 80)


def cmd_export(projects: list, conversations: list, conversations_grouped: dict, output_path: str, with_messages: bool = False):
    """Export project_conversations.json with full mapping"""
    by_id, _ = build_project_lookup(projects)

    if with_messages:
        print("Exporting with full messages (this may take a while and produce a large file)...")

    result = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_projects': len(projects),
            'total_conversations': len(conversations),
            'project_conversations': 0,
            'non_project_conversations': 0,
        },
        'projects': [],
        'non_project_conversations': [],
    }

    # Process each project
    for project in projects:
        pid = project.get('project_id')
        convs = conversations_grouped.get(pid, [])

        project_entry = {
            'project_id': pid,
            'name': project.get('name'),
            'short_url': project.get('short_url'),
            'created_at': project.get('created_at'),
            'updated_at': project.get('updated_at'),
            'last_interacted_at': project.get('last_interacted_at'),
            'num_interactions': project.get('num_interactions'),
            'memory_enabled': project.get('memory_enabled'),
            'memory_scope': project.get('memory_scope'),
            'conversation_count': len(convs),
            'conversations': [extract_conversation_summary(c, with_messages=with_messages) for c in convs],
        }
        result['projects'].append(project_entry)
        result['summary']['project_conversations'] += len(convs)

    # Sort projects by conversation count descending
    result['projects'].sort(key=lambda p: p['conversation_count'], reverse=True)

    # Handle non-project conversations
    non_project = conversations_grouped.get(None, [])
    result['summary']['non_project_conversations'] = len(non_project)

    # Group non-project conversations by gizmo_type (custom GPTs vs regular chats)
    gpt_convs = []
    regular_convs = []

    for conv in non_project:
        summary = extract_conversation_summary(conv, with_messages=with_messages)
        gizmo_type = conv.get('gizmo_type')
        if gizmo_type == 'gpt':
            summary['gizmo_id'] = conv.get('gizmo_id')
            gpt_convs.append(summary)
        else:
            regular_convs.append(summary)

    result['non_project_conversations'] = {
        'custom_gpt_conversations': {
            'count': len(gpt_convs),
            'description': 'Conversations with custom GPTs (not projects)',
            'conversations': gpt_convs,
        },
        'regular_conversations': {
            'count': len(regular_convs),
            'description': 'Regular ChatGPT conversations (no project or custom GPT)',
            'conversations': regular_convs,
        },
    }

    # Also capture orphaned project conversations (in history but project not in projects.json)
    orphaned = []
    for gizmo_id, convs in conversations_grouped.items():
        if gizmo_id is not None and gizmo_id not in by_id:
            # Check if it's a project ID pattern
            if gizmo_id.startswith('g-p-'):
                for conv in convs:
                    summary = extract_conversation_summary(conv, with_messages=with_messages)
                    summary['gizmo_id'] = gizmo_id
                    orphaned.append(summary)

    if orphaned:
        result['orphaned_project_conversations'] = {
            'count': len(orphaned),
            'description': 'Conversations linked to projects not in projects.json (possibly deleted)',
            'conversations': orphaned,
        }

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    print(f"Exported to: {output_path}")
    print()
    print("Summary:")
    print(f"  Projects: {result['summary']['total_projects']}")
    print(f"  Project conversations: {result['summary']['project_conversations']}")
    print(f"  Custom GPT conversations: {len(gpt_convs)}")
    print(f"  Regular conversations: {len(regular_convs)}")
    if orphaned:
        print(f"  Orphaned project conversations: {len(orphaned)}")

    if with_messages:
        # Calculate approximate file size
        import os
        file_size = os.path.getsize(output_path)
        if file_size > 1024 * 1024:
            print(f"  File size: {file_size / (1024 * 1024):.1f} MB")
        else:
            print(f"  File size: {file_size / 1024:.1f} KB")


def cmd_export_project(project_query: str, projects: list, conversations_grouped: dict, output_path: str = None):
    """Export a single project with full conversation messages"""
    project = find_project(project_query, projects)

    if not project:
        print(f"Error: Project '{project_query}' not found.", file=sys.stderr)
        print("\nAvailable projects:", file=sys.stderr)
        for p in projects[:10]:
            print(f"  - {p.get('name')} [{p.get('project_id')}]", file=sys.stderr)
        if len(projects) > 10:
            print(f"  ... and {len(projects) - 10} more", file=sys.stderr)
        sys.exit(1)

    pid = project.get('project_id')
    convs = conversations_grouped.get(pid, [])

    # Generate default output filename from project name
    if not output_path:
        safe_name = project.get('name', 'project').lower()
        safe_name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in safe_name)
        output_path = f"{safe_name}_conversations.json"

    print(f"Exporting project: {project.get('name')}")
    print(f"Conversations: {len(convs)}")

    result = {
        'generated_at': datetime.now().isoformat(),
        'project': {
            'project_id': pid,
            'name': project.get('name'),
            'short_url': project.get('short_url'),
            'created_at': project.get('created_at'),
            'updated_at': project.get('updated_at'),
            'last_interacted_at': project.get('last_interacted_at'),
            'num_interactions': project.get('num_interactions'),
            'memory_enabled': project.get('memory_enabled'),
            'memory_scope': project.get('memory_scope'),
        },
        'conversation_count': len(convs),
        'conversations': [],
    }

    # Sort conversations by update time descending
    convs_sorted = sorted(convs, key=lambda c: c.get('update_time') or 0, reverse=True)

    for conv in convs_sorted:
        result['conversations'].append(extract_conversation_summary(conv, with_messages=True))

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    # Calculate file size
    import os
    file_size = os.path.getsize(output_path)
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    else:
        size_str = f"{file_size / 1024:.1f} KB"

    print(f"Exported to: {output_path} ({size_str})")


def cmd_export_non_project(conversations_grouped: dict, output_path: str = None, with_messages: bool = False):
    """Export all conversations that don't belong to any project"""
    non_project = conversations_grouped.get(None, [])
    
    if not output_path:
        output_path = 'non_project_conversations.json'
    
    if with_messages:
        print("Exporting non-project conversations with full messages (this may produce a large file)...")
    
    # Group non-project conversations by type
    gpt_convs = []
    regular_convs = []
    
    for conv in non_project:
        summary = extract_conversation_summary(conv, with_messages=with_messages)
        gizmo_type = conv.get('gizmo_type')
        if gizmo_type == 'gpt':
            summary['gizmo_id'] = conv.get('gizmo_id')
            gpt_convs.append(summary)
        else:
            regular_convs.append(summary)
    
    # Sort by update time descending
    gpt_convs.sort(key=lambda c: c.get('update_time') or 0, reverse=True)
    regular_convs.sort(key=lambda c: c.get('update_time') or 0, reverse=True)
    
    result = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_non_project_conversations': len(non_project),
            'custom_gpt_conversations': len(gpt_convs),
            'regular_conversations': len(regular_convs),
        },
        'custom_gpt_conversations': {
            'count': len(gpt_convs),
            'description': 'Conversations with custom GPTs (not projects)',
            'conversations': gpt_convs,
        },
        'regular_conversations': {
            'count': len(regular_convs),
            'description': 'Regular ChatGPT conversations (no project or custom GPT)',
            'conversations': regular_convs,
        },
    }
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    # Calculate file size
    import os
    file_size = os.path.getsize(output_path)
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    else:
        size_str = f"{file_size / 1024:.1f} KB"
    
    print(f"Exported to: {output_path} ({size_str})")
    print()
    print("Summary:")
    print(f"  Custom GPT conversations: {len(gpt_convs)}")
    print(f"  Regular conversations: {len(regular_convs)}")
    print(f"  Total: {len(non_project)} non-project conversations")


def main():
    parser = argparse.ArgumentParser(
        description='ChatGPT Project Conversations Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--projects-file',
        default='projects.json',
        help='Path to projects.json (default: export-chatgpt-conversations/projects.json)'
    )
    parser.add_argument(
        '--conversations-file',
        default='conversations.json',
        help='Path to conversations.json (default: conversations.json)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # list-projects command
    subparsers.add_parser('list-projects', help='List all projects with conversation counts')

    # list command
    list_parser = subparsers.add_parser('list', help='List conversations for a project')
    list_parser.add_argument('project', help='Project name or ID')
    list_parser.add_argument(
        '--with-messages', '-m',
        action='store_true',
        help='Include full message content (truncated for display)'
    )

    # export command
    export_parser = subparsers.add_parser('export', help='Export project_conversations.json')
    export_parser.add_argument(
        '--output', '-o',
        default='project_conversations.json',
        help='Output file path (default: project_conversations.json)'
    )
    export_parser.add_argument(
        '--with-messages', '-m',
        action='store_true',
        help='Include full message content (warning: large output file)'
    )

    # export-project command
    export_project_parser = subparsers.add_parser('export-project', help='Export a single project with full messages')
    export_project_parser.add_argument('project', help='Project name or ID')
    export_project_parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output file path (default: <project_name>_conversations.json)'
    )

    # export-non-project command
    export_non_project_parser = subparsers.add_parser('export-non-project', help='Export all conversations that don\'t belong to any project')
    export_non_project_parser.add_argument(
        '--output', '-o',
        default='non_project_conversations.json',
        help='Output file path (default: non_project_conversations.json)'
    )
    export_non_project_parser.add_argument(
        '--with-messages', '-m',
        action='store_true',
        help='Include full message content (warning: large output file)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load data
    try:
        projects = load_projects(args.projects_file)
        conversations = load_conversations(args.conversations_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    conversations_grouped = group_conversations_by_project(conversations)

    # Execute command
    if args.command == 'list-projects':
        cmd_list_projects(projects, conversations_grouped)
    elif args.command == 'list':
        cmd_list_conversations(args.project, projects, conversations_grouped, with_messages=args.with_messages)
    elif args.command == 'export':
        cmd_export(projects, conversations, conversations_grouped, args.output, with_messages=args.with_messages)
    elif args.command == 'export-project':
        cmd_export_project(args.project, projects, conversations_grouped, args.output)
    elif args.command == 'export-non-project':
        cmd_export_non_project(conversations_grouped, args.output, with_messages=args.with_messages)


if __name__ == '__main__':
    main()
