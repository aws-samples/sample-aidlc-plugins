# Prerequisites for graphify-plugin — a procedure for the AI

An AI-DLC plugin cannot carry skills. graphify-plugin works without any (its stage step, converter
and rules file are complete), but people starting from scratch need help running Graphify and the
converter. That help is the optional `aidlc-graphify-code-map` skill in this folder, installed
**after** the plugin is composed.

---

## For the AI: follow this procedure

This copy was written for {{HARNESS_LABEL}}. Run every command from the project root.

Rules for every step:

- **Never overwrite.** A skill with the same name and the same content: move on. Different: show the
  difference and ask the person.
- **Never delete.** Leftovers from an older install are reported, not removed.
- **Outside this folder, change only what the steps name.**
- Report in the Step 5 format at the end.

### Step 1 — confirm the plugin is composed

```bash
grep -l "plugin:graphify-plugin:" {{H}}/aidlc-common/stages/inception/reverse-engineering.md
ls {{H}}/tools/graphify-map.ts {{H}}/knowledge/aidlc-shared/external-code-map.md
bun --version
```

- **`bun --version` fails:** the converter cannot run. Tell the person to install Bun
  (https://bun.sh): a native AI-DLC install does not include it. Continue with the other steps.
- **No marker or a missing file:** the plugin is not composed yet. Stop and say so.
- **`plugin:ua-plugin:` is also present** in that stage file: the two plugins are alternatives.
  Stop and ask which one stays.

### Step 2 — ask, then install the skill

The skill is optional. Ask the person whether to install it. If no, go to Step 3.

{{SKILLS:skill}}

A copy that differs and carries `scripts/graphify-map.ts` is the version an older installer landed,
with its own copy of the converter. This version has no script of its own: it runs the converter the
plugin installed in `{{H}}/tools/`.

### Step 3 — look for leftovers of the older install (report only)

Before graphify-plugin 0.2.0, a separate installer landed the rules and a guide outside the plugin:

```bash
ls GRAPHIFY_GUIDE.md 2>/dev/null
grep -l "^## External Code Map" aidlc/spaces/*/memory/project.md 2>/dev/null
ls aidlc/spaces/*/knowledge/aidlc-shared/external-code-map.md 2>/dev/null
```

Report each one that exists. The plugin now ships the rules file in `{{H}}/knowledge/aidlc-shared/`,
so a second copy under `aidlc/spaces/` reaches every agent twice and can drift from the plugin's.
Removing them is the person's decision; do not do it yourself.

### Step 4 — check the analysed repos (report only)

For each sibling repo that has a `graphify-out/` directory:

```bash
grep -qxE '/?graphify-out/?' <repo>/.gitignore && echo "listed" || echo "missing"
```

Do **not** edit the repo's `.gitignore` yourself: it is the person's repo. Report what is missing:
`graphify-out/` must be listed before the workflow starts, or under a strict policy CodeKB
publishing fails with `CODEKB_SOURCE_CHANGED`.

### Step 5 — verify and report

```bash
ls {{S}}/aidlc-graphify-code-map/SKILL.md      # when installed
```

Report:

```
skill: installed | already present | skipped (<reason>)
leftovers: none | <each path from Step 3>
graphify-out/ in .gitignore: <repo>: listed | missing — one line per repo
for the person: <restart the tool so it sees the new skill; install Graphify if it is not installed>
```

---

## What this folder holds

| Path | What |
|---|---|
| `requires.json` | the skill below |
| `skills/aidlc-graphify-code-map/` | How to run Graphify on a repo and convert the result (optional) |
