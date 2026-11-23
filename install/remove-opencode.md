# Remove {{PLUGIN}} {{VERSION}} from an AI-DLC project — {{PRODUCT}}

Tell the AI:

```
Read .aidlc/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.
```

---

## For the AI: follow this procedure

AI-DLC keeps no list of opencode plugins, so it stops using a plugin when the project's plugin
selection leaves it out. The steps below turn it off, delete what AI-DLC installed for it and what
its install put into the project, and leave everything else as it was.

Rules for every step:

- **Remove only what this plugin put here:** the files AI-DLC recorded for it, and the entries the
  install record lists as `installed` or `added`. An entry marked `already present` was there
  before the install; leave it.
- **Ask the person once before deleting anything**, listing what will go. When the person has
  already said yes to deleting what this procedure lists (in the message that sent you here, say),
  that is the answer: do not ask again; list what went in the report instead.
- **Use no tool the steps do not name.** No step needs Python or Node; read and edit files with
  `cat` and your own file tools. AI-DLC's native install brings neither.
- **opencode asks the person to approve `rm -r…`** (AI-DLC's `opencode.json` sets it to ask).
  Wait for the answer; never rewrite a command to get around the question. If the person declines,
  leave that folder and name it in the report.
- **Never edit `.opencode/agents/aidlc*` or `.opencode/plugin/`**, and never pass `--force`.
- `<project>` is the absolute project root. Run every command from `<project>`.
- Report in the Step 7 format at the end.

### Step 1 — check the project

```bash
cat .aidlc/tools/data/harness.json       # read it: "name" must be "opencode"
aidlc doctor 2>&1 | tail -1              # note the problem count
cat .aidlc/aidlc-plugins/{{PLUGIN}}.install-record.json
AIDLC_HARNESS_DIR=.aidlc aidlc engine plugin select
```

- Ask the person whether an intent is in progress. Removing a plugin in the middle of one can strand
  its stages; between intents is safest.
- **No install record:** the plugin was installed before records existed, or by hand. What this
  version installs besides its own files: {{REQUIRES_SUMMARY}}. For each of those that exists, ask
  the person whether this plugin's install put it there; treat only a yes as `installed`.

### Step 2 — turn the plugin off

The last command of Step 1 printed the selection and the known plugins. The plugins to keep are
the selection without `{{PLUGIN}}`, or, when it says `all enabled (no selection)`, every known
plugin except `{{PLUGIN}}`. `aidlc` always stays.

```bash
AIDLC_HARNESS_DIR=.aidlc aidlc engine plugin select <the plugins to keep, comma-separated>
grep -l "plugin:{{PLUGIN}}:" .aidlc/aidlc-common/stages/*/*.md      # prints nothing now
```

If `select` refuses because a workflow in progress depends on the plugin, show its message and stop.

### Step 3 — delete what AI-DLC installed for it

```bash
cat .aidlc/tools/data/plugin-owned-{{PLUGIN}}.json
```

Delete every file listed under `files` (`path`, relative to the project; a plugin's agents are
among them, under `.opencode/agents/`), one `rm <path>` per file, then these:

```bash
rm .aidlc/tools/data/plugin-compose-{{PLUGIN}}.json .aidlc/tools/data/plugin-files-{{PLUGIN}}.json .aidlc/tools/data/plugin-owned-{{PLUGIN}}.json
```

Remove the directories those deletions left empty (`rmdir`, never `rm -rf` here). Then rebuild
AI-DLC's stage graph, which still lists the deleted stage files:

```bash
aidlc engine graph compile
aidlc engine graph compile --check       # prints nothing
```

### Step 4 — what the install record lists

For each entry with status `installed` or `added`:

- **A skill:** delete its folder (`rm -rf <path>`; the path is under `.aidlc/skills/`).
- **An MCP server:** remove that one key from `"mcp"` in the project-root `opencode.json` (or
  `opencode.jsonc`), change nothing else, and read the file back. When `"mcp"` is then empty and
  it was not in the file before the install, remove the empty `"mcp": {}` too.
- **A line:** remove exactly that line or entry from its file (`.aidlc-source-paths.json`), and read
  the file back. When `.aidlc-source-paths.json` is then down to `"version"` and an empty
  `"exclude"` list (no `"paths"`, no other entry), delete the whole file: an empty one was not there
  before the install.

### Step 5 — the record and this folder

Delete `.aidlc/aidlc-plugins/{{PLUGIN}}.install-record.json`, then the folder
`.aidlc/aidlc-plugins/{{PLUGIN}}/` (`rm -rf`; this file is in it, and you have read it to the end).

### Step 6 — verify

```bash
AIDLC_HARNESS_DIR=.aidlc aidlc engine plugin list     # {{PLUGIN}} is not listed
AIDLC_HARNESS_DIR=.aidlc aidlc engine plugin select   # {{PLUGIN}} is not known
aidlc engine graph compile --check                    # prints nothing
aidlc doctor 2>&1 | tail -1                           # same problem count as Step 1
```

### Step 7 — report

```
harness: {{PRODUCT}}
plugin: {{PLUGIN}} — turned off and removed | <what stopped it>
selection now: <the list>
files deleted: <count> from plugin-owned, 3 records
from the install record: <each skill, server and line, and what you did with it> | no record
doctor: <before> → <after> problems
```

Then tell the person:

- This project now has an explicit plugin list (`select` keeps one once it has been set). A plugin
  installed later with its own INSTALL.md adds itself to that list.
- If doctor warns `Hook failures … review-freeze … "State file not found"`: in a project with no
  intent, AI-DLC's review-freeze hook records one for each file the agent deletes after `select`.
  It is a warning, not a problem, and it clears 24 hours after the last one.
- Start `opencode` again so it drops the removed skills and servers.
