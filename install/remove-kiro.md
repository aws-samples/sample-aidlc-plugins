# Remove {{PLUGIN}} {{VERSION}} from an AI-DLC project — {{PRODUCT}}

Tell the AI:

```
Read .kiro/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.
```

---

## For the AI: follow this procedure

Kiro has no plugin store, so AI-DLC stops using a plugin when the project's plugin selection leaves
it out. The steps below turn it off, delete what AI-DLC installed for it and what its install put
into the project, and leave everything else as it was.

Rules for every step:

- **Remove only what this plugin put here:** the files AI-DLC recorded for it, and the entries the
  install record lists as `installed` or `added`. An entry marked `already present` was there
  before the install; leave it.
- **Ask the person once before deleting anything**, listing what will go.
- **Use no tool the steps do not name.** No step needs Python or Node; read and edit files with
  `cat` and your own file tools. AI-DLC's native install brings neither.
- **Never edit `.kiro/agents/aidlc*`**, and never pass `--force`.
- `<project>` is the absolute project root. Run every command from `<project>`.
- Report in the Step 7 format at the end.

### Step 1 — check the project

```bash
cat .kiro/tools/data/harness.json        # read it: "name" must be "{{HARNESS}}"
aidlc doctor 2>&1 | tail -1              # note the problem count
cat .kiro/aidlc-plugins/{{PLUGIN}}.install-record.json
AIDLC_HARNESS_DIR=.kiro aidlc engine plugin select
```

- Ask the person whether an intent is in progress. Removing a plugin in the middle of one can strand
  its stages; between intents is safest.
- **No install record:** the plugin was installed before records existed, or by hand. What this
  version installs besides its own files: {{REQUIRES_SUMMARY}}. For each of those that exists, ask
  the person whether this plugin's install put it there; treat only a yes as `installed`.

### Step 2 — turn the plugin off

The second command of Step 1 printed the selection and the known plugins. The plugins to keep are
the selection without `{{PLUGIN}}`, or, when it says `all enabled (no selection)`, every known
plugin except `{{PLUGIN}}`. `aidlc` always stays.

```bash
AIDLC_HARNESS_DIR=.kiro aidlc engine plugin select <the plugins to keep, comma-separated>
grep -l "plugin:{{PLUGIN}}:" .kiro/aidlc-common/stages/*/*.md      # prints nothing now
```

If `select` refuses because a workflow in progress depends on the plugin, show its message and stop.

### Step 3 — delete what AI-DLC installed for it

```bash
cat .kiro/tools/data/plugin-owned-{{PLUGIN}}.json
```

Delete every file listed under `files` (`path`, relative to the project), then these:

```bash
rm .kiro/tools/data/plugin-compose-{{PLUGIN}}.json .kiro/tools/data/plugin-files-{{PLUGIN}}.json .kiro/tools/data/plugin-owned-{{PLUGIN}}.json
```

<!-- harness: kiro-ide -->
Leave `.kiro/hooks/aidlc-{{PLUGIN}}-compose.json` to the person and do not try to delete it:
AI-DLC's guard refuses an agent's delete under `.kiro/hooks/` (measured on 2.11.4 with Kiro CLI
3.2.0). Step 7 asks the person to delete it. Until they do, doctor reports one problem more than
in Step 1, `Native command trust is incomplete: 1 Bun-shaped entry`, which is that hook.

<!-- /harness -->
Remove the directories those deletions left empty (`rmdir`, never `rm -rf` here). Then rebuild
AI-DLC's stage graph, which still lists the deleted stage files:

```bash
aidlc engine graph compile
aidlc engine graph compile --check       # prints nothing
```

### Step 4 — what the install record lists

For each entry with status `installed` or `added`:

- **A skill:** delete its folder (`rm -rf <path>`; the path is under `.kiro/skills/`).
- **An MCP server:** `kiro-cli mcp remove --name <name> --scope workspace`, then `cat
  .kiro/settings/mcp.json` and check the other entries are still there. Without `kiro-cli` (Kiro
  IDE only): remove that one key from the file; if the write is refused, show the person the key.
  When the file then reads `{"mcpServers": {}}` and nothing else, Step 7 asks the person to delete
  it (you cannot write under `.kiro/settings/`).
<!-- harness: kiro -->
  The AI-DLC agent JSONs keep their `"@<name>"` grant. Leave it: `aidlc config` never drops a
  grant an agent file already names (a teammate's server stays granted), and Kiro CLI V2 ignores a
  grant for a server it does not have (both measured on 2.11.4). Do not run `aidlc config` for it.
<!-- /harness -->
- **A line:** remove exactly that line or entry from its file, and read the file back.

### Step 5 — the record and this folder

Delete `.kiro/aidlc-plugins/{{PLUGIN}}.install-record.json`, then the folder
`.kiro/aidlc-plugins/{{PLUGIN}}/` (this file is in it; you have read it to the end).

### Step 6 — verify

```bash
AIDLC_HARNESS_DIR=.kiro aidlc engine plugin list     # {{PLUGIN}} is not listed
AIDLC_HARNESS_DIR=.kiro aidlc engine plugin select   # {{PLUGIN}} is not known
aidlc engine graph compile --check                   # prints nothing
aidlc doctor 2>&1 | tail -1                          # same problem count as Step 1
```
<!-- harness: kiro-ide -->

On this harness doctor shows one problem more than in Step 1 until the person deletes the compose
hook (Step 3). Any other new problem: show it.
<!-- /harness -->

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

<!-- harness: kiro-ide -->
- **Delete `.kiro/hooks/aidlc-{{PLUGIN}}-compose.json` yourself**, outside the agent (a terminal or
  Kiro's file explorer), before the next session: its command points at the deleted plugin folder
  and fails at every session start. Then `aidlc doctor` shows the Step 1 problem count again.
<!-- /harness -->
- When `.kiro/settings/mcp.json` now reads `{"mcpServers": {}}` and nothing else: delete that file
  too (the agent cannot write there). Skip this line when it still lists a server.
- This project now has an explicit plugin list (`select` keeps one once it has been set). A plugin
  installed later with its own INSTALL.md adds itself to that list.
- If doctor warns `Hook failures … review-freeze … "State file not found"`: in a project with no
  intent, AI-DLC's review-freeze hook records one for each file the agent deletes. It is a warning,
  not a problem, and it clears 24 hours after the last one.
<!-- harness: kiro-ide -->
- In Kiro IDE, reload the window (`Developer: Reload Window`); in Kiro CLI, start `kiro-cli` again.
<!-- /harness -->
<!-- harness: kiro -->
- Start `kiro-cli --v2` again.
<!-- /harness -->

Measured on AI-DLC 2.11.4 (Kiro IDE harness, a plugin that adds stages): after Steps 2 and 3, the
plugin's stages, runners and table rows are gone, `graph compile --check` is clean and doctor shows
0 problems. Without `graph compile`, doctor fails with "Orphan stage files".
