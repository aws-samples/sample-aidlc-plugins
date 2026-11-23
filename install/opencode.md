# Install {{PLUGIN}} {{VERSION}} into an AI-DLC project — {{PRODUCT}}

This folder came out of `{{ZIP}}`, unzipped at the project root,
so it sits at `.aidlc/aidlc-plugins/{{PLUGIN}}/`. Tell the AI:

```
Read .aidlc/aidlc-plugins/{{PLUGIN}}/INSTALL.md to the end and follow it.
```

---

## For the AI: follow this procedure

opencode has no plugin store that AI-DLC can read, and AI-DLC's engine sits in `.aidlc/` (not
`.opencode/`) on this harness. The plugin lives in this folder, inside the project, and AI-DLC
composes it from here. The steps below compose it and then install what the plugin cannot carry.

Rules for every step:

- **Never overwrite, never delete.** When something with the same name exists and differs, show
  the difference and ask the person.
- **Outside this folder, change only what the steps name.**
- **Install no tool the steps do not name.** No step needs Python or Node; read files with `cat`
  or your own file reader. AI-DLC's native install brings neither.
- **Never edit `.opencode/agents/aidlc*` or `.opencode/plugin/`.** They are AI-DLC's.
- **opencode may ask the person to approve a command.** AI-DLC's `opencode.json` sets some commands
  to ask (for example `rm -r…`). That is expected: wait for the answer; never rewrite a command to
  get around the question.
- `<project>` is the absolute project root. Run every command from `<project>`.
- Report in the Step 8 format at the end.

### Step 1 — check the project

```bash
cat .aidlc/tools/data/harness.json     # read it: "name" must be "opencode"
aidlc --version
aidlc doctor 2>&1 | tail -1        # note the problem count
```

- Not `opencode`: this zip is for AI-DLC's opencode harness. Stop and tell the person to use the
  zip built for the harness `aidlc config` set up for this project.
- `aidlc` not found: stop and say so.
- `aidlc` older than 2.11.4: this procedure was measured on 2.11.4. Tell the person and ask whether
  to continue.
- Ask the person whether an intent is in progress, even when the files show none (they may have a
  session open elsewhere). Installing changes the stages; between intents is safest.

**Alternatives:** `ua-plugin` and `graphify-plugin` are two tools for the same step. If you are
installing one of them and the other is present, stop and ask which one stays:

```bash
grep -o 'plugin:\(ua\|graphify\)-plugin:' .aidlc/aidlc-common/stages/inception/reverse-engineering.md | sort -u
ls -d .aidlc/aidlc-plugins/*/ 2>/dev/null
```

### Step 2 — compose it into AI-DLC

```bash
aidlc engine plugin sync --harness-dir .aidlc --plugin-root ./.aidlc/aidlc-plugins/{{PLUGIN}}
AIDLC_HARNESS_DIR=.aidlc aidlc engine plugin list
ls .aidlc/tools/data/plugin-compose-{{PLUGIN}}.json
find .aidlc -name '*.drops'
```

Expect `plugin sync complete: 1 plugin(s)`, the plugin listed with its version under `COMPOSED`
(`not compared: no host plugin list` is normal on opencode), the compose record present, and no
`.drops` file.

If sync exits non-zero, show its last lines and stop. Sync is a transaction: one dropped
contribution rolls the whole sync back, so nothing half-applied is left behind.

### Step 3 — this project's plugin selection

```bash
AIDLC_HARNESS_DIR={{H}} aidlc engine plugin select
```

- `Current plugin selection: all enabled (no selection)`, or a list that names `{{PLUGIN}}`: nothing
  to do.
- A list without `{{PLUGIN}}`: someone chose this project's plugins explicitly, and a plugin outside
  that list is composed but stays off. Ask the person whether to add it; on a yes run
  `AIDLC_HARNESS_DIR={{H}} aidlc engine plugin select <that list>,{{PLUGIN}}` and the first command
  again. Note it for the install record.

### Step 4 — keep the plugin's agents out of AI-DLC's code scan

{{PERSONA_EXCLUDES}}

### Step 5 — what the plugin cannot carry

If `prerequisites/INSTALL.md` exists in this folder, read it to the end and follow it now. It was
written for this harness and says where each skill and server goes.

### Step 6 — write the install record

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
  "mcp": [{"name": "<name>", "where": "<file>", "status": "added | already present"}],
  "lines": [{"file": "<file>", "added": "<the exact line or entry>"}],
  "files_created": ["<a file this install created>"]
}
```

Use empty lists for what this plugin did not touch. `files_created` lists only files that did not
exist when this install first wrote to them (check before that first write); `REMOVE.md` deletes an
emptied file only when it is listed there. Read the file back and check it is valid JSON.

Then check doctor:

```bash
aidlc doctor 2>&1 | tail -1        # same problem count as Step 1
```

### Step 7 — keep this folder

AI-DLC composes the plugin from `.aidlc/aidlc-plugins/{{PLUGIN}}/`. Do not delete or move it, and
tell the person the same. It also holds `REMOVE.md`, the procedure that takes the plugin out again.
It is not project code: AI-DLC's reverse engineering skips `.aidlc/`. If the project is shared
through git, committing this folder gives everyone the plugin.

### Step 8 — report

```
harness: {{PRODUCT}}
plugin: {{PLUGIN}} <"version" in .aidlc/tools/data/plugin-compose-{{PLUGIN}}.json>
compose: composed, drops 0 | <the sync error>
selection: all enabled | already listed | added | left off (<reason>)
agents excluded: <the lines added to .aidlc-source-paths.json> | none needed | declined
prerequisites: <the report from prerequisites/INSTALL.md> | none
record: .aidlc/aidlc-plugins/{{PLUGIN}}.install-record.json
doctor: <before> → <after> problems
```

Then tell the person what happens next:

- opencode runs no plugin hook when a session starts, so nothing composes the plugin again by
  itself. After unzipping a newer version, or after upgrading AI-DLC, run Step 2 again. Start
  `opencode` again so it sees any new skills or servers.
- To take the plugin out later: `Read .aidlc/aidlc-plugins/{{PLUGIN}}/REMOVE.md to the end and follow it.`

---

## Where things end up

| What | Where | Seen by reverse engineering |
|---|---|---|
| the plugin | `.aidlc/aidlc-plugins/{{PLUGIN}}/` | no — harness directory |
| composed stages, runners, tools, knowledge | `.aidlc/` | no — harness directory |
| the plugin's agents, if it has any | `.opencode/agents/<agent>.md` | source boundary yes, until Step 4 excludes them; CodeKB snapshot no |
| skills from `prerequisites/` | `.aidlc/skills/` | no — harness directory |
| MCP servers from `prerequisites/` | `opencode.json` at the project root, under `"mcp"` | no |
| install record | `.aidlc/aidlc-plugins/{{PLUGIN}}.install-record.json` | no — harness directory |

Measured on AI-DLC 2.11.4 with opencode 1.19.5: project type and the CodeKB source snapshot are
unchanged after install; the source boundary gains only a plugin's own agent files, which the
`.aidlc-source-paths.json` exclude takes out again (the file itself then counts as source, as on
Codex).
