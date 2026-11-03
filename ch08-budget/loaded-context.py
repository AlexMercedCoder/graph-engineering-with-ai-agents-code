#!/usr/bin/env python3
"""List what Claude Code loaded into a session, request by request.

Claude Code keeps a session file for every conversation under
~/.claude/projects/<project-folder>/<session-id>.jsonl. Besides the messages, it records
what the harness attached to the context: the instruction files it loaded at the start,
each path-scoped rule and nested CLAUDE.md it added after a file read, changes to the
skill listing, compaction boundaries, and what came back after a compaction (files it
read again and invoked skills it re-attached). This script prints those events in order,
with the payload of each model request, so you can see what each request carried and why.

Usage:
  python3 loaded-context.py ~/.claude/projects/<project-folder>/<session-id>.jsonl
  python3 loaded-context.py --latest <project-dir>    newest session for that project

The session file also holds your account details; this script prints none of them.
Standard library only.
"""
import argparse
import glob
import json
import os
import re
import sys


def latest(project_dir):
    folder = os.path.expanduser('~/.claude/projects/' + re.sub(r'[^A-Za-z0-9]', '-', os.path.abspath(project_dir)))
    files = sorted(glob.glob(folder + '/*.jsonl'), key=os.path.getmtime)
    if not files:
        sys.exit(f'no session files in {folder}')
    return files[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--latest', metavar='PROJECT_DIR')
    args = ap.parse_args()
    path = latest(args.latest) if args.latest else args.path
    if not path:
        ap.error('give a session file or --latest <project-dir>')
    root = None
    pending = None  # [message id, request number, payload, tools]
    request = 0

    def flush():
        nonlocal pending
        if pending:
            _, n, payload, tools = pending
            print(f'request {n:>3}  payload {payload:>8,}' + (f'  then {", ".join(tools)}' if tools else ''))
            pending = None

    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        root = root or e.get('cwd')
        rel = (lambda p: os.path.relpath(p, root) if root and p else p)
        if e.get('type') == 'assistant' and not e.get('isSidechain'):
            msg = e.get('message', {})
            tools = [c.get('name') for c in msg.get('content', []) if c.get('type') == 'tool_use']
            if pending and pending[0] == msg.get('id'):
                pending[3].extend(tools)
                continue
            flush()
            u = msg.get('usage') or {}
            payload = (u.get('input_tokens') or 0) + (u.get('cache_read_input_tokens') or 0) + (u.get('cache_creation_input_tokens') or 0)
            request += 1
            pending = [msg.get('id'), request, payload, tools]
            continue
        a = e.get('attachment') if isinstance(e.get('attachment'), dict) else None
        if a and a.get('type') in ('instructions', 'nested_memory', 'skill_listing', 'file', 'invoked_skills'):
            flush()
            t = a.get('type')
            if t == 'instructions':
                files = ', '.join(f"{rel(f.get('path'))} ({len(f.get('content', ''))} chars)" for f in a.get('files', []))
                print(f'  load    instructions: {files}')
            elif t == 'nested_memory':
                c = a.get('content') or {}
                size = len(c.get('content', '')) if isinstance(c, dict) else 0
                print(f'  load    path-scoped: {rel(a.get("path"))} ({size} chars)')
            elif t == 'file':
                print(f'  load    file re-read: {rel(a.get("filename"))} ({len(json.dumps(a.get("content", "")))} chars)')
            elif t == 'invoked_skills':
                for sk in a.get('skills', []):
                    print(f'  load    invoked skill: {sk.get("name")} ({len(sk.get("content", ""))} chars)')
            else:
                names = re.findall(r'^- ([\w:-]+):', a.get('content', ''), re.M)
                print(f'  load    skill listing: {len(names)} skills, {len(a.get("content", ""))} chars')
        if e.get('type') == 'system' and e.get('subtype') == 'compact_boundary':
            flush()
            m = e.get('compactMetadata') or {}
            print(f"  ------  compaction ({m.get('trigger')}), {m.get('preTokens')} tokens before")
    flush()

if __name__ == '__main__':
    main()
