# Prerequisites for visual-mockups — a procedure for the AI

An AI-DLC plugin cannot carry skills or MCP servers. visual-mockups' HTML preview needs neither: its
design rules ship with the plugin as knowledge for the design agent. Only the Figma path needs
something installed here, **after** the plugin is composed:

| Path | Needs |
|---|---|
| HTML preview | nothing: the rules come with the plugin |
| Figma file | the `figma` MCP server, Figma's skills `figma-use`, `figma-generate-design`, `figma-create-new-file` (fetched from Figma's repository at a pinned commit, not shipped), and a Dev or Full seat on a paid Figma plan |

Without Figma, the stages still offer HTML or "neither", and the markdown mockup still reaches code.

---

## For the AI: follow this procedure

This copy was written for {{HARNESS_LABEL}}. Run every command from the project root.

Rules for every step:

- **Never overwrite.** A skill or server entry with the same name and the same content: move on.
  Different: show the difference and ask the person.
- **Never delete,** except the temporary directory you create for a fetch. Leftovers from an older
  install are reported, not removed.
- **Outside this folder, change only what the steps name.** Anything you download goes in a new,
  empty temporary directory outside the project.
- **Never edit `{{H}}/agents/aidlc*`**, and do not ask the person to.
- Report in the Step 5 format at the end.

### Step 1 — confirm the plugin is composed

```bash
grep -l "plugin:visual-mockups:" \
  {{H}}/aidlc-common/stages/ideation/rough-mockups.md \
  {{H}}/aidlc-common/stages/inception/refined-mockups.md \
  {{H}}/aidlc-common/stages/construction/code-generation.md
ls {{H}}/knowledge/aidlc-design-agent/visual-mockups-design.md
```

All four files must be listed. If any is missing, the plugin is not composed yet: stop and say so.

### Step 2 — ask about Figma

<!-- harness: claude codex kiro-ide kiro -->
Ask the person whether to prepare the Figma path as well. HTML needs nothing more.

- **Yes:** say first that Figma needs a Dev or Full seat on a paid Figma plan, and that by using the
  Figma MCP server and Figma's skills they agree to the Figma Developer Terms
  (https://www.figma.com/legal/developer-terms/). Then go to Step 3.
- **No:** go to Step 4.
<!-- /harness -->
<!-- harness: opencode -->
On opencode the Figma path is not available, so do not offer it and skip Step 3: Figma's MCP server
refuses opencode's sign-in (its client registration answers `403 Forbidden` to the client name
`OpenCode`, whatever the callback; measured 2026-11-16 with opencode 1.19.5). Tell the person that
this project gets the HTML preview only, even if they asked for Figma, and go to Step 4.
<!-- /harness -->

### Step 3 — Figma: the skills and the server

<!-- harness: claude -->
**Already provided?** Figma's own Claude Code plugin brings both the skills and the server:

```bash
grep -o '"figma@[^"]*"' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/installed_plugins.json" 2>/dev/null
```

If that prints a name, skip the rest of this step, say so in the report, and tell the person to
check it is enabled in `/plugin`.

<!-- /harness -->
{{SKILLS:figma}}

Then the server:

{{MCP:figma}}

The conductor calls Figma at rough-mockups and refined-mockups, and `aidlc-developer-agent` at
code-generation, where it reads the design for a UI unit. Each call asks the person first.
<!-- harness: codex -->
Codex's agent files name no MCP servers; whether its subagents reach Figma has not been measured.
<!-- /harness -->

### Step 4 — look for what older versions left (report only)

```bash
ls -d {{S}}/frontend-design 2>/dev/null
find aidlc/spaces -name 'mockup-visual-ref*.md' 2>/dev/null
grep -l "mockup-visual-ref" {{H}}/aidlc-common/stages/*/*.md 2>/dev/null
```

Report each one. Remove none of them yourself.

- **`frontend-design`:** visual-mockups before 0.3.0 installed this skill for the HTML preview. This
  version does not use it. Something else may: removing it is the person's decision.
- **A `mockup-visual-ref*.md` record:** 0.1.0's pointer name. An intent still in progress will not
  find it at code-generation; renaming it to `visual-mockups-ref*.md` is the person's decision.
- **A stage file naming `mockup-visual-ref`:** 0.1.0 was composed into this tree and its
  `produces`/`consumes` are still in that stage's frontmatter. The fix is in `../README.md`
  ("Upgrading from 0.1.0"); tell the person, do not edit the stage file.
<!-- harness: kiro-ide kiro -->
- **`"@figma"` added by hand to `.kiro/agents/aidlc*`** (what an older version of this procedure
  asked for): the next `aidlc config` stops with `locally modified or unowned` on those files. Tell
  the person to run `aidlc config --project-dir "<project>" --dry-run`; when the conflict list names
  only those agent files, they move them out of the project and run `aidlc config` again, without
  `--force`.
<!-- /harness -->

### Step 5 — verify and report

```bash
ls {{S}}/figma-use/SKILL.md {{S}}/figma-generate-design/SKILL.md {{S}}/figma-create-new-file/SKILL.md   # Figma only
```

Report:

```
paths: HTML only | HTML and Figma
figma skills: installed from figma/mcp-server-guide@5f3024c3decd | already present | provided by Figma's Claude Code plugin | skipped (<reason>)
figma server: added (<where>) | already present (<where>) | skipped (<reason>)
older leftovers: none | <each path from Step 4>
```

Then tell the person what is left for them when they chose Figma:

- **Figma account:** the first Figma call asks them to authorize.
<!-- harness: claude -->
- Restart Claude Code, then finish Figma's authorization in `/mcp`.
<!-- /harness -->
<!-- harness: codex -->
- Restart Codex, then run `codex mcp login figma` to authorize.
<!-- /harness -->
<!-- harness: kiro-ide -->
- Kiro IDE: run `Developer: Reload Window` and check in the MCP panel that `figma` is connected and
  authorized. Kiro CLI v3: restart `kiro-cli`, then authorize `figma` when it asks (`/mcp`).
- Each Figma call asks for approval first. That is AI-DLC's default, not a fault.
<!-- /harness -->
<!-- harness: kiro -->
- Restart `kiro-cli --v2`, then authorize `figma` when it asks (`/mcp`).
- Each Figma call asks for approval first. That is AI-DLC's default, not a fault.
<!-- /harness -->
<!-- harness: opencode -->
- Figma is not available on opencode (Step 2); the stages offer the HTML preview or neither.
<!-- /harness -->

---

## What this folder holds

| Path | What |
|---|---|
| `requires.json` | the Figma skills (repository, pinned commit, tree hash) and the `figma` server |

Figma's skills are not shipped: Figma publishes them in `figma/mcp-server-guide` without a licence
file, so Step 3 fetches them from there at the commit this version was measured with.
