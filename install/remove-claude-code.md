# Remove {{PLUGIN}} {{VERSION}} from an AI-DLC project — Claude Code

Tell the AI:

```
Read .claude/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.
```

---

## For the AI: follow this procedure

Claude Code installed the plugin for this project only (local scope). The steps below uninstall it
there, let AI-DLC take out everything it composed for it, remove what its install put into the
project, and leave everything else as it was.

Rules for every step:

- **Remove only what this plugin put here:** what AI-DLC composed for it, and the entries the
  install record lists as `installed` or `added`. An entry marked `already present` was there
  before the install; leave it.
- **Ask the person once before deleting anything**, listing what will go.
- **Use no tool the steps do not name.** No step needs Python or Node; read and edit files with
  `cat` and your own file tools. AI-DLC's native install brings neither.
- Never pass `--force`.
- `<project>` is the absolute project root; `<CFG>` is `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`. Run
  every command from `<project>`.
- Report in the Step 7 format at the end.

### Step 1 — check the project

```bash
cat .claude/tools/data/harness.json        # read it: "name" must be "claude"
aidlc doctor 2>&1 | tail -1                # note the problem count
cat .claude/aidlc-plugins/{{PLUGIN}}.install-record.json
AIDLC_HARNESS_DIR=.claude aidlc engine plugin list
```

- Ask the person whether an intent is in progress. Removing a plugin in the middle of one can strand
  its stages; between intents is safest.
- **No install record:** the plugin was installed before records existed, or by hand. What this
  version installs besides its own files: {{REQUIRES_SUMMARY}}. For each of those that exists, ask
  the person whether this plugin's install put it there; treat only a yes as `installed`.

### Step 2 — uninstall it and let AI-DLC take it out

```bash
claude plugin uninstall {{PLUGIN}}@{{PLUGIN}} --scope local
AIDLC_HARNESS_DIR=.claude aidlc engine plugin list
```

`{{PLUGIN}}` now shows `installed plugin missing from your host's list`. Before the next command,
check that no **other** plugin shows that status: the command removes every plugin Claude Code no
longer lists. If another one does, stop and ask the person.

```bash
AIDLC_HARNESS_DIR=.claude AIDLC_HARNESS_NAME=claude aidlc engine plugin sync --prune-missing --yes
grep -l "plugin:{{PLUGIN}}:" .claude/aidlc-common/stages/*/*.md      # prints nothing now
ls .claude/tools/data/plugin-compose-{{PLUGIN}}.json 2>/dev/null     # gone
```

Expect `pruned 1 missing plugin(s)`. That removes the plugin's stages, runners, agents, knowledge,
tools and fragments, and AI-DLC's records of them. If the record says `"selection_added": true`,
also run `AIDLC_HARNESS_DIR=.claude aidlc engine plugin select` and, when it still names
`{{PLUGIN}}`, select the same list without it.

### Step 3 — what the install record lists

For each entry with status `installed` or `added`:

- **A skill:** delete its folder (`rm -rf <path>`; the path is under `.claude/skills/`).
- **An MCP server:** `claude mcp remove --scope local <name>`.
- **A line:** remove exactly that line or entry from its file, and read the file back.

### Step 4 — the record and this folder

Delete `.claude/aidlc-plugins/{{PLUGIN}}.install-record.json`, then the folder
`.claude/aidlc-plugins/{{PLUGIN}}/` (this file is in it; you have read it to the end).

### Step 5 — what stays outside the project

`<CFG>/aidlc-plugins/{{PLUGIN}}/` and the marketplace named `{{PLUGIN}}` belong to the person, not
the project: another project of theirs may still use them. Do not remove them. Tell the person that
when no project uses the plugin any more, `claude plugin marketplace remove {{PLUGIN}}` and deleting
that folder clear them.

### Step 6 — verify

```bash
AIDLC_HARNESS_DIR=.claude aidlc engine plugin list    # {{PLUGIN}} is not listed
aidlc doctor 2>&1 | tail -1                           # same problem count as Step 1
```

### Step 7 — report

```
harness: Claude Code
plugin: {{PLUGIN}} — uninstalled and pruned | <what stopped it>
from the install record: <each skill, server and line, and what you did with it> | no record
left for the person: <CFG>/aidlc-plugins/{{PLUGIN}}/, marketplace {{PLUGIN}}
doctor: <before> → <after> problems
```

Then tell the person to restart Claude Code in this project.

Measured on AI-DLC 2.11.4 (a plugin that adds stages): after Step 2 every file AI-DLC composed for
the plugin is gone, `tables.md` no longer lists its stages, and doctor shows 0 problems.
