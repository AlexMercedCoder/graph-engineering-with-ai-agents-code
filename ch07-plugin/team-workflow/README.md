# team-workflow

The Part 2 execution graph, packaged. Install it, and a colleague gets the same
skills, workers, and safety hooks you have.

    claude --plugin-dir ./team-workflow      # try it without installing
    claude plugin validate ./team-workflow   # check structure before publishing

Components live at the plugin root. Only `plugin.json` goes inside
`.claude-plugin/`, which is the single most common packaging mistake: a plugin
with `skills/` nested under `.claude-plugin/` loads successfully with nothing in it.

Hook paths use `${CLAUDE_PLUGIN_ROOT}`, not `${CLAUDE_PROJECT_DIR}`. A plugin is
installed into a versioned cache directory whose name changes on every update, so
a project-relative path works on the machine that built it and nowhere else.
