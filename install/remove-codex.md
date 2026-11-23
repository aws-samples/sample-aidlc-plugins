# Remove {{PLUGIN}} {{VERSION}} from an AI-DLC project — Codex

Tell the AI:

```
Read .codex/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.
```

---

## For the AI: follow this procedure

Codex installs a plugin for the person, in every Codex project of theirs, so there are two ways to
remove it. The steps below ask which one, take the plugin out, remove what its install put into
this project, and leave everything else as it was.

Rules for every step:

- **Remove only what this plugin put here:** what AI-DLC composed for it, and the entries the
  install record lists as `installed` or `added`. An entry marked `already present` was there
  before the install; leave it.
- **Ask the person once before deleting anything**, listing what will go.
- **Use no tool the steps do not name.** No step needs Python or Node; read and edit files with
  `cat` and your own file tools. AI-DLC's native install brings neither.
- Never pass `--force`.
- `<project>` is the absolute project root; `<CX>` is `${CODEX_HOME:-$HOME/.codex}`. Run every
  command from `<project>`. Writing under `.agents/` needs approval to run outside Codex's sandbox;
  ask for it when a step needs it.
- Report in the Step 7 format at the end.

### Step 1 — check the project, and ask which removal

```bash
cat .codex/tools/data/harness.json        # read it: "name" must be "codex"
aidlc doctor 2>&1 | tail -1               # note the problem count
cat .codex/aidlc-plugins/{{PLUGIN}}.install-record.json
AIDLC_HARNESS_DIR=.codex aidlc engine plugin list
AIDLC_HARNESS_DIR=.codex aidlc engine plugin select
```

- Ask the person whether an intent is in progress. Removing a plugin in the middle of one can strand
  its stages; between intents is safest.
- **No install record:** the plugin was installed before records existed, or by hand. What this
  version installs besides its own files: {{REQUIRES_SUMMARY}}. For each of those that exists, ask
  the person whether this plugin's install put it there; treat only a yes as `installed`.
- Ask: **only this project**, or **every Codex project of theirs**?

### Step 2 — take the plugin out

**Only this project.** The plugin stays installed for the person, so its hook composes it again at
every session start; turning it off is what lasts. The plugins to keep are the selection without
`{{PLUGIN}}`, or, when it says `all enabled (no selection)`, every known plugin except `{{PLUGIN}}`.
`aidlc` always stays.

```bash
AIDLC_HARNESS_DIR=.codex aidlc engine plugin select <the plugins to keep, comma-separated>
grep -l "plugin:{{PLUGIN}}:" .codex/aidlc-common/stages/*/*.md      # prints nothing now
```

AI-DLC's files for the plugin stay in `.codex/`, switched off. Tell the person that this project
now has an explicit plugin list.

**Every project.** Uninstall it for the person, then let AI-DLC take it out of this project:

```bash
codex plugin remove {{PLUGIN}}@{{PLUGIN}}
AIDLC_HARNESS_DIR=.codex aidlc engine plugin list
```

`{{PLUGIN}}` now shows `installed plugin missing from your host's list`. Check that no **other**
plugin shows that status: the next command removes every plugin Codex no longer lists. If another
one does, stop and ask the person.

```bash
AIDLC_HARNESS_DIR=.codex AIDLC_HARNESS_NAME=codex aidlc engine plugin sync --prune-missing --yes
grep -l "plugin:{{PLUGIN}}:" .codex/aidlc-common/stages/*/*.md      # prints nothing now
```

Expect `pruned 1 missing plugin(s)`. Every other project where it was composed needs the same
`sync --prune-missing --yes` there, and its own REMOVE.md for that project's skills and lines: tell
the person.

### Step 3 — what the install record lists

For each entry with status `installed` or `added`:

- **A skill:** delete its folder (`rm -rf <path>`; the path is under `.agents/skills/`).
- **An MCP server:** delete its `[mcp_servers.<name>]` table from `.codex/config.toml`: the header
  line, the lines under it up to the next table, and the blank line the install put before it. The
  file then ends the way it did before the install: its last table, then a single newline. Read
  the file back.
- **A line:** remove exactly that line or entry from its file (`.aidlc-source-paths.json`,
  `.gitignore`), and read the file back. When `.aidlc-source-paths.json` is then down to
  `"version"` and an empty `"exclude"` list (no `"paths"`, no other entry), delete the whole file
  only when the install record lists it under `files_created`; otherwise leave it (it was there
  before the install, or the record is older than `files_created`) and say so in the report.

### Step 4 — the record and this folder

Delete `.codex/aidlc-plugins/{{PLUGIN}}.install-record.json`, then the folder
`.codex/aidlc-plugins/{{PLUGIN}}/` (this file is in it; you have read it to the end).

### Step 5 — what stays outside the project

`<CX>/aidlc-plugins/{{PLUGIN}}/` and the marketplace named `{{PLUGIN}}` belong to the person. After
"every project", tell them `codex plugin marketplace remove {{PLUGIN}}` and deleting that folder
clear them. After "only this project" they are still in use; leave them.

### Step 6 — verify

```bash
AIDLC_HARNESS_DIR=.codex aidlc engine plugin list    # every project: not listed; this project: listed, switched off
grep -l "plugin:{{PLUGIN}}:" .codex/aidlc-common/stages/*/*.md     # prints nothing
aidlc doctor 2>&1 | tail -1                          # same problem count as Step 1
```

### Step 7 — report

```
harness: Codex
plugin: {{PLUGIN}} — off in this project | removed for the person and pruned here | <what stopped it>
from the install record: <each skill, server and line, and what you did with it> | no record
left for the person: <other projects to prune> | <CX>/aidlc-plugins/{{PLUGIN}}/, marketplace {{PLUGIN}}
doctor: <before> → <after> problems
```

Then tell the person to restart Codex in this project.

Measured on AI-DLC 2.11.4 with Codex 0.169 (a plugin that adds stages): after `codex plugin remove`
and the prune, every file AI-DLC composed for the plugin is gone, including its runners in
`.agents/skills/`, and doctor shows 0 problems.
