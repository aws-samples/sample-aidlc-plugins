# Prerequisites for ua-plugin — a procedure for the AI

An AI-DLC plugin cannot carry skills. ua-plugin works without any (its stage steps, converter and
rules file are complete), but people starting from scratch need help running Understand-Anything
and the converter. That help is the optional `aidlc-ua-code-map` skill in this folder, installed
**after** the plugin is composed.

---

## For the AI: follow this procedure

This copy was written for {{HARNESS_LABEL}}. Run every command from the project root.

Rules for every step:

- **Never overwrite.** A skill with the same name and the same content: move on. Different: show the
  difference and ask the person.
- **Never delete** without the person's yes (Step 2 asks about one old folder). Other leftovers are
  reported, not removed.
- **Outside this folder, change only what the steps name.**
- Report in the Step 6 format at the end.

### Step 1 — confirm the plugin is composed

```bash
grep -l "plugin:ua-plugin:" {{H}}/aidlc-common/stages/inception/reverse-engineering.md
ls {{H}}/tools/ua-code-map.ts {{H}}/knowledge/aidlc-shared/external-code-map.md
bun --version
```

- **`bun --version` fails:** the converter cannot run. Tell the person to install Bun
  (https://bun.sh): a native AI-DLC install does not include it. Continue with the other steps.
- **No marker or a missing file:** the plugin is not composed yet. Stop and say so.
- **`plugin:graphify-plugin:` is also present** in that stage file: the two plugins are
  alternatives. Stop and ask which one stays.

### Step 2 — the skill's old name

Before 0.5.0 the same skill was called `aidlc-external-code-map`.

```bash
ls -d {{S}}/aidlc-external-code-map 2>/dev/null
```

If it is there, tell the person it is this skill under its old name and ask whether to remove it
once the new one is installed (both would answer the same requests). Remove it only on a yes:
`rm -rf {{S}}/aidlc-external-code-map`. If your tool refuses, name the folder in the report for the
person to delete.

### Step 3 — ask, then install the skill

The skill is optional. Ask the person whether to install it. If no, go to Step 4.

{{SKILLS:skill}}

A copy that differs and carries `scripts/ua-code-map.ts` is the single-repo version from an older
release. This version has no script of its own: it runs the converter the plugin installed in
`{{H}}/tools/`.

### Step 4 — look for leftovers of the older install (report only)

ua-plugin 0.1.0 relied on a separate installer that landed the rules and a guide outside the plugin:

```bash
ls UNDERSTANDING_GUIDE.md 2>/dev/null
grep -l "^## External Code Map" aidlc/spaces/*/memory/project.md 2>/dev/null
ls aidlc/spaces/*/knowledge/aidlc-shared/external-code-map.md 2>/dev/null
```

Report each one that exists. The plugin now ships the rules file in `{{H}}/knowledge/aidlc-shared/`,
so an older copy under `aidlc/spaces/` reaches every agent as well, and that copy predates the
multi-repo rules. Removing them is the person's decision; do not do it yourself.

### Step 5 — check the analysed repos (report only)

For each sibling repo that has a `.ua/` directory:

```bash
git -C <repo> check-ignore -q .ua/ && echo "ignored" || echo "not ignored"
```

This succeeds when `.ua/` is listed in the repo's `.gitignore` or in its `.git/info/exclude` (local,
nothing to commit). Do **not** edit either yourself: it is the person's repo. Report what is
missing: git must ignore `.ua/` before the workflow starts, or under a strict policy CodeKB
publishing fails with `CODEKB_SOURCE_CHANGED`.

### Step 6 — verify and report

```bash
ls {{S}}/aidlc-ua-code-map/SKILL.md      # when installed
```

Report:

```
skill: installed | already present | skipped (<reason>)
old skill name: not present | removed | kept (<reason>)
leftovers: none | <each path from Step 4>
.ua/ ignored by git: <repo>: ignored | not ignored — one line per repo
for the person: <restart the tool so it sees the new skill; install Understand-Anything if it is not installed>
```

---

## What this folder holds

| Path | What |
|---|---|
| `requires.json` | the skill below |
| `skills/aidlc-ua-code-map/` | How to run Understand-Anything on each repo and convert each result (optional) |
