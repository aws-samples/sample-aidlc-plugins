# Install {{PLUGIN}} {{VERSION}} into an AI-DLC project — Codex

This folder came out of `{{ZIP}}`, unzipped at the project root, so it
sits at `.codex/aidlc-plugins/{{PLUGIN}}/`. Tell the AI:

```
Read .codex/aidlc-plugins/{{PLUGIN}}/INSTALL.md to the end and follow it.
```

---

## For the AI: follow this procedure

Codex installs the plugin from its own plugin store, which keeps the plugin's files outside the
project. A Codex plugin is installed **for the user, not for one project**: once installed, every
AI-DLC project this person opens in Codex composes it at session start. The steps below register
this folder as a local marketplace, install the plugin, compose it into this project, and then
install what the plugin cannot carry.

Rules for every step:

- **Never overwrite, never delete.** When something with the same name exists and differs, show
  the difference and ask the person.
- **Outside this folder, change only what the steps name.**
- **Install no tool the steps do not name.** No step needs Python or Node; read files with `cat`
  or your own file reader. AI-DLC's native install brings neither, and on a new Mac `python3`
  opens an install dialog.
- `<project>` is the absolute project root; `<CX>` is `${CODEX_HOME:-$HOME/.codex}`. Run every
  command from `<project>`.
- Report in the Step 11 format at the end.

### Step 1 — check the project

```bash
cat .codex/tools/data/harness.json     # read it: "name" must be "codex"
aidlc --version
codex --version
aidlc doctor 2>&1 | tail -1        # note the problem count
```

- Not `codex`: this zip is for Codex. Stop and tell the person which zip matches their tool.
- `aidlc` or `codex` not found: stop and say so.
- `aidlc` older than 2.11.2: this procedure was measured on 2.11.2 to 2.11.4. Tell the person and ask whether
  to continue.
- Tell the person the plugin will be installed for every Codex project of theirs, and ask before
  going on. Ask too whether an intent is in progress, even when the files show none (they may have a
  session open elsewhere): installing changes the stages, so between intents is safest.

**Alternatives:** `ua-plugin` and `graphify-plugin` are two tools for the same step. If you are
installing one of them and the other is present, stop and ask which one stays:

```bash
grep -o 'plugin:\(ua\|graphify\)-plugin:' .codex/aidlc-common/stages/inception/reverse-engineering.md | sort -u
codex plugin list 2>/dev/null | grep -E '^(ua|graphify)-plugin@'
```

### Step 2 — copy this folder to the user's plugin sources

Codex keeps one source folder per marketplace name for the whole user and refuses a second one.
Keep that source where it outlives this project:

```bash
SRC="<CX>/aidlc-plugins/{{PLUGIN}}"
ls "$SRC" 2>/dev/null && diff -rq .codex/aidlc-plugins/{{PLUGIN}} "$SRC"
codex plugin marketplace list 2>/dev/null | grep -A1 '{{PLUGIN}}'
```

- `$SRC` missing: `mkdir -p "<CX>/aidlc-plugins" && cp -R .codex/aidlc-plugins/{{PLUGIN}} "$SRC"`
- `$SRC` present, no diff output: same version, move on.
- `$SRC` present and different: another version is installed for this user. Show the `"version"`
  in `$SRC/.codex-plugin/plugin.json` and in this folder's, and ask the person. Upgrading in place
  has not been measured.
- A `{{PLUGIN}}` marketplace already registered from another folder: show it and ask. Codex will
  refuse the add in Step 3 until that one is removed, and removing it is the person's decision.

### Step 3 — install the plugin

Skip what is already done:

```bash
codex plugin list 2>/dev/null | grep '^{{PLUGIN}}@{{PLUGIN}}'   # "installed, enabled" → skip this step
codex plugin marketplace add "$SRC"
codex plugin add {{PLUGIN}}@{{PLUGIN}}
```

Expect `Installed plugin root: <CX>/plugins/cache/{{PLUGIN}}/{{PLUGIN}}/<version>`.

### Step 4 — compose it into AI-DLC

```bash
AIDLC_HARNESS_DIR=.codex AIDLC_HARNESS_NAME=codex aidlc engine plugin sync
AIDLC_HARNESS_DIR=.codex aidlc engine plugin list
ls .codex/tools/data/plugin-compose-{{PLUGIN}}.json
find .codex -name '*.drops'
```

Expect `plugin sync complete`, the plugin listed as `current`, the compose record present, and no
`.drops` file. Sync composes every Codex plugin this person has installed, so other plugins may be
listed too.

If sync exits non-zero, show its last lines and stop. Sync is a transaction: one dropped
contribution rolls the whole sync back, so nothing half-applied is left behind.

**`EPERM` (or "Operation not permitted") on a path under `.codex/` or `.agents/`:** that is Codex's
sandbox, not the plugin. `workspace-write` does not let commands write those folders: measured on
Codex 0.166 for `.agents/` and on 0.169 for `.codex/aidlc-common/` (sync renames stage files
there). Do not look for a way around it and do not stop the install for it: ask the person to
approve running the same sync command outside the sandbox, and run it again. If they decline, tell
them the plugin's own hook runs outside the sandbox and composes it at the start of the next
interactive `codex` session; then they run `AIDLC_HARNESS_DIR=.codex aidlc engine plugin list`
there to check it reads `current`, and the remaining steps wait until then.

### Step 5 — this project's plugin selection

```bash
AIDLC_HARNESS_DIR={{H}} aidlc engine plugin select
```

- `Current plugin selection: all enabled (no selection)`, or a list that names `{{PLUGIN}}`: nothing
  to do.
- A list without `{{PLUGIN}}`: someone chose this project's plugins explicitly, and a plugin outside
  that list is composed but stays off. Ask the person whether to add it; on a yes run
  `AIDLC_HARNESS_DIR={{H}} aidlc engine plugin select <that list>,{{PLUGIN}}` and the first command
  again. Note it for the install record.

### Step 6 — keep the plugin's runners out of the code scan

{{RUNNER_EXCLUDES}}
### Step 7 — what the plugin cannot carry

If `prerequisites/INSTALL.md` exists in this folder, read it to the end and follow it now. It was
written for Codex and says where each skill and server goes. Skills go into the project's
`.agents/skills/`, where Codex reads them for this project only. Writing there needs the same
approval to run outside the sandbox as Step 4's sync; ask for it the same way.

### Step 8 — write the install record

Write `{{H}}/aidlc-plugins/{{PLUGIN}}.install-record.json`, next to this folder, replacing an older
one. It lists what this install put into the project, so that `REMOVE.md` can take out exactly that
and nothing that was there before:

```json
{
  "plugin": "{{PLUGIN}}",
  "version": "{{VERSION}}",
  "harness": "{{HARNESS}}",
  "date": "<YYYY-MM-DD>",
  "selection_added": false,
  "skills": [{"name": "<name>", "path": "<path>", "source": "<repo>@<commit> | bundled", "status": "installed | already present"}],
  "mcp": [{"name": "<name>", "where": "<file, or claude mcp local scope>", "status": "added | already present"}],
  "lines": [{"file": "<file>", "added": "<the exact line or entry>"}]
}
```

Use empty lists for what this plugin did not touch. Read the file back and check it is valid JSON.

### Step 9 — verify

```bash
aidlc doctor 2>&1 | tail -1        # same problem count as Step 1
```

A plugin that adds stages or scopes rewrites `.agents/skills/aidlc/tables.md`. On 2.11.2 doctor then
warned `AI-DLC files: 1 changed in this project, so aidlc config keeps it and stops`; that warning
was wrong about the stop (`aidlc config` afterwards ran with `conflict=0`, kept the plugin, and the
warning cleared). From 2.11.3 it does not appear. Never suggest `aidlc config --force`.

### Step 10 — keep this folder

Codex loads the plugin from its own copy, but keep `.codex/aidlc-plugins/{{PLUGIN}}/` and tell the
person the same. A teammate who clones the project installs from this folder with the same one
line, without the zip. It also holds `REMOVE.md`, the procedure that takes the plugin out again,
next to the install record. It is not project code: AI-DLC's reverse engineering skips `.codex/`.

### Step 11 — report

```
harness: Codex
plugin: {{PLUGIN}} <"version" in .codex/tools/data/plugin-compose-{{PLUGIN}}.json>
source: <CX>/aidlc-plugins/{{PLUGIN}} — copied | already there
installed: for this user | already installed
compose: current, drops 0 | <the sync error>
selection: all enabled | already listed | added | left off (<reason>)
runners kept out of the scan: added | declined | none
prerequisites: <the report from prerequisites/INSTALL.md> | none
record: .codex/aidlc-plugins/{{PLUGIN}}.install-record.json
doctor: <before> → <after> problems
```

Then tell the person:

- Start Codex interactively in this project (`codex`, not `codex exec`). The first time, it asks
  to trust the folder and shows "Hooks need review" for AI-DLC's own hooks: choose **Trust and
  continue**, then **Trust all and continue**. The plugin adds a SessionStart hook of its own; when
  Codex shows "Hooks need review — 1 hook is new or changed" for it (measured on Codex 0.167), open
  `/hooks`, trust it (`t`), and it runs at every session start from then on. `codex exec` does
  not run plugin hooks; after an upgrade there, run Step 4 again.
- To take the plugin out later: `Read .codex/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.`

---

## Where things end up

| What | Where | Seen by reverse engineering |
|---|---|---|
| plugin files Codex loads | `<CX>/plugins/cache/{{PLUGIN}}/{{PLUGIN}}/<version>/` | no — outside the project |
| marketplace source and Codex's install entry | `<CX>/aidlc-plugins/{{PLUGIN}}/`, `<CX>/config.toml` | no — outside the project |
| this plugin's folder and install record | `.codex/aidlc-plugins/{{PLUGIN}}/`, `.codex/aidlc-plugins/{{PLUGIN}}.install-record.json` | no — harness directory |
| composed stages, tools, knowledge | `.codex/` | no — harness directory |
| stage runners of a plugin that adds stages | `.agents/skills/<stage>/` | CodeKB no; source boundary no once Step 6 adds them to `.aidlc-source-paths.json` |
| skills from `prerequisites/` | `.agents/skills/<name>/` | no, once Step 7 adds them to `.aidlc-source-paths.json` (and `.gitignore` for names not starting with `aidlc`) |
| MCP servers from `prerequisites/` | `.codex/config.toml` | no — harness directory |

Measured on AI-DLC 2.11.2 with Codex 0.166.0: project type and the CodeKB source snapshot are
unchanged after install, and `aidlc config` afterwards reports no conflict. On 2.11.4 an
`"exclude"` entry in `.aidlc-source-paths.json` took `.agents/skills/` folders out of the source
boundary (the file itself is then one new root file); the CodeKB snapshot does not read that file
but already leaves out `.agents/skills/aidlc*` and generated runners, and git-ignored paths.
