"""Synthetic skills with descriptions shaped like Chapter 4's specific version, for measuring listing cost only."""
import os
AREAS = ['billing', 'invoices', 'refunds', 'shipping', 'inventory', 'catalog', 'search', 'pricing',
         'accounts', 'sessions', 'permissions', 'audit', 'reports', 'exports', 'imports', 'webhooks',
         'notifications', 'emails', 'scheduler', 'cache', 'queue', 'metrics', 'logging', 'migrations',
         'fixtures', 'seeds', 'docs', 'changelog', 'release', 'feature-flags', 'rate-limits', 'tenants',
         'payments', 'orders', 'users', 'auth', 'routes', 'repositories', 'services', 'tests']
VERBS = [('review', 'Reviews', 'reports problems as a written list', 'Does not modify files.'),
         ('explain', 'Explains', 'describes how it works and what depends on it, as prose', 'Reads only.'),
         ('fix', 'Fixes', 'edits the files and runs the affected tests', 'Modifies files.'),
         ('scaffold', 'Scaffolds', 'creates the files and a passing test', 'Modifies files.')]

def desc(area, verb):
    key, Verb, out, side = verb
    return (f"{Verb} the {area} module named in the request and {out}. Use when the user asks to {key} "
            f"{area} code, asks what is wrong with {area}, or names a file under src/{area}/. {side} "
            f"Use the sibling {area} skills for other kinds of {area} work.")

def all_skills():
    return [(f'{v[0]}-{a}', desc(a, v)) for a in AREAS for v in VERBS]

def write(d, name, description, body='Follow the project conventions for this kind of work.', extra=''):
    os.makedirs(f'{d}/.claude/skills/{name}', exist_ok=True)
    open(f'{d}/.claude/skills/{name}/SKILL.md', 'w').write(f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# {name}\n\n{body}\n")

def make_skills(d, count):
    for name, description in all_skills()[:count]:
        write(d, name, description)

def make_grouped(d, count, groups):
    skills = all_skills()[:count]
    per = count // groups
    for g in range(groups):
        members = skills[g * per:(g + 1) * per]
        areas = sorted({m[0].split('-', 1)[1] for m in members})
        os.makedirs(f'{d}/.claude/skill-groups/group-{g+1}', exist_ok=True)
        menu = []
        for name, description in members:
            open(f'{d}/.claude/skill-groups/group-{g+1}/{name}.md', 'w').write(f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n")
            menu.append(f'- {name}: `.claude/skill-groups/group-{g+1}/{name}.md`')
        write(d, f'group-{g+1}', f"Reviews, explains, fixes, or scaffolds code in the {', '.join(areas)} modules. Use when the request names one of those areas or a file under them. Read the matching procedure file before starting.",
              body='Pick the procedure that matches the request and read its file before you start.\n\n' + '\n'.join(menu))
