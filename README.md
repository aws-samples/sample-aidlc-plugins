# sample-aidlc-plugins

Sample plugins for [AI-DLC](https://github.com/awslabs/aidlc-workflows) v2, the AI-driven
development lifecycle. They show how to extend AI-DLC through its plugin mechanism without
changing the engine: adding prose to an existing stage, adding new stages and a new scope, and
shipping knowledge files and a small tool with a plugin. Each plugin is packaged as one zip per tool
and installed by the AI itself, which follows the `INSTALL.md` in the zip; a `REMOVE.md` beside it
takes the plugin out again.

| Plugin | What it shows |
|---|---|
| `visual-mockups` | Prose added to three existing stages: the mockup stages offer an HTML preview (or a Figma file) and carry it into code generation |
| `ua-plugin` | Reverse engineering starts from an [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) code map, through a shipped converter tool and a rules file |
| `graphify-plugin` | The same for a [Graphify](https://github.com/Graphify-Labs/graphify) graph; an alternative to `ua-plugin`, not a layer on it |
| `project-overview` | Four new stages, one at the end of each phase, that keep one project overview up to date |
| `requirements-handoff` | A new no-code scope for a product owner: requirements, a clickable wireframe and a development request for a delivery team |

This is sample code, for non-production usage. You should work with your security and legal teams
to meet your organizational security, regulatory and compliance requirements before deployment. It
is not part of AI-DLC or an AWS service.

## Prerequisites

- AI-DLC 2.11.4 installed (`aidlc --version`) and set up in your project with `aidlc config`, for
  one of: Claude Code, Codex, Kiro (Kiro IDE, or Kiro CLI on its v3 or V2 engine), or opencode.
- To build the zips: [bun](https://bun.sh), Python 3 and [uv](https://docs.astral.sh/uv/).
- `ua-plugin` and `graphify-plugin` need bun at run time, and the code-map tool itself, which you
  install and run yourself.

## Use

Build the zips with the plugin tools of your AI-DLC install (`<project>/<harness directory>/tools`,
for example `.claude/tools`), unzip the one for your tool at the project root, and give your AI
one line:

```bash
uv run python scripts/package-plugin.py --tools <project>/.claude/tools --out dist visual-mockups
cd <project> && unzip <path>/dist/aidlc-visual-mockups-<version>-claude.zip
```

```
Read .claude/aidlc-plugins/visual-mockups/INSTALL.md to the end and follow it.
```

The zip suffix names the AI-DLC harness: `claude`, `codex`, `kiro-ide` (Kiro IDE and Kiro CLI v3),
`kiro` (Kiro CLI V2) and `opencode`. The folder it lands in, and the line to give, are listed under
"Distribute" below. To take a plugin out: `Read <harness directory>/aidlc-plugins/<plugin>/REMOVE.md
to the end and follow it.`

---

## For plugin authors — authoring form and apply procedure

The authoring form of five AI-DLC plugins, plus the drivers that judge the result
of putting them on a tree or shell.

```
visual-mockups/     gives the mockup stages a visual surface and carries the mockup into code
ua-plugin/          lets reverse-engineering use an external structural map as an index — Understand-Anything
graphify-plugin/    the same seam for Graphify — an ALTERNATIVE to ua-plugin, not a layer on it
project-overview/   a stage at the end of each phase that keeps one cumulative project overview per space
requirements-handoff/ a no-code scope for a product owner: requirements, screen design and a clickable wireframe for a delivery team
install/            the INSTALL.md and REMOVE.md each packaged zip carries, one pair per tool (Claude Code, Codex, Kiro, opencode)
scripts/            packaging, judgement and MCP registry drivers
```

All five ship **no compose hook** and are built and tested with the plugin tools of the release
they target (see "Which tools"); the builder injects the bundled hook, so
`aidlc engine plugin sync` installs them. `visual-mockups` 0.1.0 and
`graphify-plugin` 0.1.0 carried a pinned older hook that sync refuses; their
READMEs say how to upgrade a tree that has them.

🔴🔴 **`ua-plugin` and `graphify-plugin` are alternatives.** They contribute the same anchor of the
same stage for two different tools, so a tree carrying both hands the Developer two indexes with two
provenance chains. **Compose exactly one of them into a tree.** Nothing in compose enforces it —
each owns its own sentinel — but both `prerequisites/INSTALL.md` procedures stop on a tree that
carries the other.

| Driver | What it does |
|---|---|
| `scripts/package-plugin.py` | builds one zip per harness — projection, `prerequisites/` and the matching `install/` doc as `INSTALL.md` (see "Distribute") |
| `scripts/check-plugin-anchors.py` | `--pre` every declared anchor resolves in the compose base · `--post` every fragment actually landed |
| `scripts/merge-mcp-registry-kiro.py` | union-merges MCP entries into `.kiro/settings/mcp.json`, never overriding a stock key; copies each source block verbatim, so its `"disabled": true` (both the stock and our source registry carry it) stays |
| `scripts/merge-mcp-registry-claude.py` | the same for a claude tree's root `.mcp.json`, dropping the `disabled` key |
| `scripts/apply-mcp-registry-policy.py` | narrows the merged registry to a chosen server set and adds the `context7` header |

The MCP drivers serve the distribution build. A person installing `visual-mockups` gets the `figma`
entry from its `INSTALL.md` instead.

A plugin here is **not** a layer of the distributed tree — it is applied on
demand, so a committed tree does not carry one. The tradeoff is explicit: when a
plugin was a layer, that layer's `spec/manifest.json` pinned the apply result as
a sha map, so "spec output == compose output" was proved mechanically. That proof
is gone; apply is now judged by running the table below. What is gained is that
the plugin is a choice rather than a property of the tree.

---

## Which tools — `<tools-dir>`

Every command below that runs `bun <tools-dir>/aidlc-plugin-*.ts` needs the plugin tools **of the
release you target**: a tree of that release (`<project>/<harness>/tools`, e.g. one made with
`aidlc config` by that `aidlc` binary), or a checkout of that release's tag with its generated data
(`plugin-targets.json`, `data/plugin-hooks-template/`). The builder copies the compose hook and the
Kiro IDE hook registration from wherever it runs, so older tools build an older hook (before 2.11.3,
no `"timeout"`). **Do not assume a local engine checkout matches the installed `aidlc`**: check
`aidlc --version` against the tools' release.

---

## Distribute — a zip per tool, one prompt to install

AI-DLC has no command a person types to install a plugin. Package each plugin as one zip per tool;
the person unzips it at the project root and gives the AI one line.

```bash
uv run python scripts/package-plugin.py --tools <tools-dir> \
  --out <dir outside this repo> visual-mockups ua-plugin graphify-plugin project-overview requirements-handoff
```

| Zip | Lands at | The person tells the AI |
|---|---|---|
| `aidlc-<p>-<v>-claude.zip` | `.claude/aidlc-plugins/<p>/` | `Read .claude/aidlc-plugins/<p>/INSTALL.md to the end and follow it.` |
| `aidlc-<p>-<v>-codex.zip` | `.codex/aidlc-plugins/<p>/` | `Read .codex/aidlc-plugins/<p>/INSTALL.md to the end and follow it.` |
| `aidlc-<p>-<v>-kiro-ide.zip` — Kiro IDE, and Kiro CLI on its v3 engine | `.kiro/aidlc-plugins/<p>/` + `.kiro/hooks/aidlc-<p>-compose.json` | `Read .kiro/aidlc-plugins/<p>/INSTALL.md to the end and follow it.` |
| `aidlc-<p>-<v>-kiro.zip` — Kiro CLI on its V2 engine | `.kiro/aidlc-plugins/<p>/` | same |
| `aidlc-<p>-<v>-opencode.zip` | `.aidlc/aidlc-plugins/<p>/` (opencode's engine directory is `.aidlc/`) | `Read .aidlc/aidlc-plugins/<p>/INSTALL.md to the end and follow it.` |

The suffix is the AI-DLC harness, not the tool: `kiro-ide` serves Kiro IDE and Kiro CLI v3. For a
distribution that ships one harness only, `--harness <h> --plain-name` names the zip
`aidlc-<p>-<v>.zip`; its INSTALL.md names that file.

Each zip carries three documents written for its harness: `INSTALL.md` (from `install/<tool>.md`), `prerequisites/INSTALL.md` and `REMOVE.md` (from `install/remove-<tool>.md`). `scripts/prereqs.py` fills them from the plugin's need list `prerequisites/requires.json` (skills, pinned to a commit and tree hash when fetched, and MCP entries) and keeps only the `<!-- harness: … -->` blocks for that harness. The install writes a record, `<H>/aidlc-plugins/<p>.install-record.json`, of each skill, server and line it `installed`, `added` or found `already present`; `REMOVE.md` deletes only the first two kinds. The person keeps the unzipped folder: the record and `REMOVE.md` live beside it, and teammates install from it.

The four tools install differently, and `install/` holds one procedure for each:

| | Claude Code (`install/claude-code.md`) | Codex (`install/codex.md`) | Kiro: `kiro-ide` and `kiro` harnesses (`install/kiro.md`) | opencode (`install/opencode.md`) |
|---|---|---|---|---|
| install | copy to `<config>/aidlc-plugins/<p>/`, local marketplace, `claude plugin install --scope local` | copy to `$CODEX_HOME/aidlc-plugins/<p>/`, `codex plugin add` — **for the user, every project** | none — the plugin stays in `.kiro/aidlc-plugins/<p>/` | none — the plugin stays in `.aidlc/aidlc-plugins/<p>/` |
| compose | the AI runs `aidlc engine plugin sync`; the plugin's SessionStart hook after that | same; plugin hooks run in interactive `codex`, not in `codex exec` | the AI runs sync with `AIDLC_PLUGIN_ROOT`; Kiro IDE's compose hook after that, Kiro CLI has none | the AI runs `sync --harness-dir .aidlc --plugin-root <folder>`; no hook, so again after an upgrade |
| skills / MCP | `.claude/skills/` · `claude mcp add --scope local` | `.agents/skills/` + an `exclude` line in `.aidlc-source-paths.json` · `.codex/config.toml` | `.kiro/skills/` · `kiro-cli mcp add --scope workspace` (Kiro IDE without `kiro-cli`: `.kiro/settings/mcp.json`) | `.aidlc/skills/` · `"mcp"` in the project-root `opencode.json`; a plugin's agents in `.opencode/agents/` get an `exclude` line |
| unzipped folder afterwards | **keep** | **keep** | **keep** | **keep** |
| remove | `REMOVE.md`: `claude plugin uninstall --scope local`, then `sync --prune-missing --yes` | `REMOVE.md`: this project only → `select`; every project → `codex plugin remove`, then prune in each | `REMOVE.md`: `select` the kept plugins, delete `plugin-owned` files, `graph compile`; the person deletes the Kiro IDE hook json | `REMOVE.md`: as on Kiro, with no hook json; opencode asks the person before each `rm -r…` |

🔴 **Nothing may land outside the harness directory or the user's tool config.** Measured on 2.11.2:
a folder at the project root with a `tests/` directory or a `.ts` file turns a new project
brownfield; a server in the project's `.mcp.json` and a skill in `.agents/skills/` enter the source
boundary. With the placements above, project type, the CodeKB source snapshot and the source
boundary stay unchanged on all four harnesses, and an AI following only `INSTALL.md` installed
`visual-mockups` + `ua-plugin` end to end on Claude Code, Codex and Kiro CLI. The one exception is
engine behaviour: on Codex, a plugin that adds stages puts its runners in `.agents/skills/`, and on
opencode a plugin that adds agents puts them in `.opencode/agents/`; both enter the source boundary
until `.aidlc-source-paths.json` excludes them, which the install offers. opencode's `opencode.json`
at the project root is AI-DLC's own file and outside the boundary, so its `"mcp"` entries are too
(measured on 2.11.4).

On opencode, visual-mockups offers the HTML preview only: Figma's MCP server refuses opencode's
sign-in (its client registration answers `403 Forbidden` to the client name `OpenCode`, measured
2026-11-16 with opencode 1.19.5).

---

## Apply — once per plugin (development)

```bash
TOOLS=<tools-dir>      # see "Which tools"
TARGET=<project root>
HD=.kiro            # .claude for a claude tree

# 1. 🔴 PRE-FLIGHT — measure that anchors resolve AND bind to the intended step
uv run python scripts/check-plugin-anchors.py --pre "$TARGET" --plugin-root <plugin>
#    🔴🔴 "resolved" is not "bound correctly" — **read the titles.** A stage that drops
#    a step renumbers everything after it: one anchor then vanishes (and would be
#    dropped) while another survives and binds to the wrong step. The silent one is
#    worse. ⇒ **an anchor means a title, not a number.** (A vanished anchor is a
#    `[degraded]` drop: direct compose still exits 0, sync rejects the result.)
#    On exit 1 the fix belongs in the authoring form (`<plugin>/contributions/`),
#    not in the tree.

# 2. Validate and build the projection for the harness
bun $TOOLS/aidlc-plugin-validate.ts <plugin>          # VALID, one compose-hook-absent warning
bun $TOOLS/aidlc-plugin-build.ts    <plugin> <harness> <out>   # claude, codex, kiro-ide; Kiro CLI V2 = kiro-v2 (2.11.4+), kiro (earlier)

# 3. Install the projection the host's way and sync — the steps in install/<tool>.md
#    (Claude Code / Codex: local marketplace + install, then sync; Kiro: drop the
#    projection's .kiro folder into the project, then)
aidlc engine plugin sync --harness-dir .kiro --plugin-root ./.kiro/aidlc-plugins/<plugin>
#    🔴 `aidlc engine plugin sync --help` RAN a sync on 2.11.3 (no help flag); 2.11.4 prints
#    the usage. Run sync only inside the scratch tree.

# 4. Prerequisites the seam cannot carry — tell the AI:
#    "Read <plugin>/prerequisites/INSTALL.md to the end and follow it."
#    (visual-mockups, ua-plugin, graphify-plugin; project-overview and requirements-handoff have none)

# 5. 🔴 Judge by the artifact — exit code is not a judgement
uv run python scripts/check-plugin-anchors.py --post "$TARGET" --plugin-root <plugin>
```

- **Sync is a transaction.** Every selected plugin composes in a staging copy first; one
  `[degraded]` drop rejects the staged result before anything is committed, and the drops file is
  thrown away with the staging copy — read the sync's own error line.
- **A file sync has no record of installing is never overwritten.** That is how an older plugin
  version's tool, composed by the pinned hook, blocks the first sync of the new one; the plugin's
  README names the file to delete.
- `bun $TOOLS/aidlc-plugin-test.ts <plugin> --install <project-root> --harness <harness>` runs the
  same build and compose in a staging copy (drops, graph compile, idempotent second compose) and
  leaves the install untouched.

### Prerequisites ship in `prerequisites/`

🔴 **The seam can ship neither skills nor MCP servers.** The valid
`aidlc.contributes` keys are `stages · overlays · agents · scopes · sensors ·
knowledge · tools`, plus `memory` from 2.11.4 (the validator refused it up to 2.11.3). Rules files go through
`knowledge`. What is left — skills, and for `visual-mockups` the `figma` MCP entry —
sits in each plugin's `prerequisites/` with an `INSTALL.md` the AI follows **after**
the plugin is composed. Neither the builder nor compose reads `prerequisites/`.

| Plugin | `prerequisites/` holds | Fetched instead of shipped |
|---|---|---|
| `visual-mockups` | nothing (the HTML design rules are plugin knowledge) | Figma's three skills, from `figma/mcp-server-guide` at a pinned commit (no licence file) |
| `ua-plugin` | `aidlc-ua-code-map` (optional) | — |
| `graphify-plugin` | `aidlc-graphify-code-map` (optional) | — |

⭐ **No procedure touches an always-on instruction file.** `AGENTS.md` and `CLAUDE.md`
stay byte-identical to stock: a pointer there is read by every stage, while a
skill's own `description` costs nothing. The trade-off is deliberate — a user who
never mentions a code map is never told the wiring exists, the same way
`visual-mockups` waits to be asked.

## 🔴 Judgement table — do not trust exit 0

| Item | How to measure | Expected |
|---|---|---|
| stage count unchanged | `stage-graph.json` array length · slug set | both unchanged for the three overlay-only plugins |
| prose splice landed | `check-plugin-anchors.py --post` | per file, **sentinels = fragments×2** (open+close) · **`### Step Nb` headings owned by the plugin = fragment count**. 🔴**Never gate on the total heading count** — that is the host stage's own numbering and upstream moves it (a hardcoded value produces false FAILs) |
| drops | sync's exit and error line · `find "$TARGET" -name '*.drops'` | sync `complete`, **0** drops files |
| visual-mockups seam | `produces`/`consumes` delta | `rough` produces += `visual-mockups-ref` · `refined` produces += `visual-mockups-ref-refined`, consumes += `visual-mockups-ref` · `code-generation` consumes += both plus `mockups`, `wireframes`, all optional. No `mockup-visual-ref` left anywhere (0.1.0's name) |
| ua-plugin | `tools/ua-code-map.ts` + `knowledge/aidlc-shared/external-code-map.md` installed · `stage-graph.json` **unchanged** | no `adds`, so the graph does not move |
| graphify-plugin | `tools/graphify-map.ts` + `knowledge/aidlc-shared/external-code-map.md` installed · `stage-graph.json` **unchanged** | same shape as the row above |
| prerequisites | the `INSTALL.md` report | every line accounted for; MCP file parses, no other key changed. The added `figma` entry has no `disabled` key; the stock Kiro CLI entries keep their `"disabled": true` |
| 0 regressions | `doctor` · `graph compile --check` | **same doctor count as before apply** · exit 0. 🔴Do not record absolute doctor numbers here |
| idempotent | `aidlc-plugin-test.ts` | `Idempotent second compose: true` |

Measured 2026-10-26 on AI-DLC v2.11.1 (claude and kiro-ide trees packaged from the tag):
`visual-mockups` 0.2.0 and `graphify-plugin` 0.2.0 validate `VALID` and test `CLEAN`, sync with the
`aidlc` 2.11.1 binary into the same tree side by side, and both `INSTALL.md` procedures run through.

## Known · deliberately untouched

- **Overlay-only plugins are selectable once composed.** Since `v2.10.1-preview.20261004.1`
  (upstream #1675, so every 2.11 release) the known-plugin list also reads compose's records under `tools/data/` (`plugin-contrib-`, `plugin-owned-`,
  `plugin-compose-<p>.json`), not only stage and scope owners. Measured 2026-11-06 on a
  kiro-ide 2.11.3 project with visual-mockups composed: `aidlc engine plugin select`
  prints `Known plugins: aidlc, visual-mockups`. Earlier engines listed only stage and scope
  owners, so an overlay-only plugin did not appear there.
- **`visual-mockups` deliberately reverses two earlier positions** — it puts the
  plugin back in, and it does touch the MCP file. The patch layer itself still
  does not: the `figma` key is added only when a person asks for the Figma path.
- **The code-map plugins do not restate the rules in the stage.** How to treat a map
  belongs to `knowledge/aidlc-shared/external-code-map.md`, which each ships and
  compose installs into `<harness>/knowledge/aidlc-shared/`; the delegated
  personas' **MANDATORY** "Delegated knowledge preflight" reads that directory, so
  the rules reach reverse-engineering. The fragments carry only WHERE/WHEN (the
  conductor procedure).

---

## What has been tested

On AI-DLC 2.11.4, an AI installed each plugin from its zip into a new project by following
`INSTALL.md`, and then removed it again by following `REMOVE.md`, on these tools:

| Tool | AI-DLC harness | Measured on |
|---|---|---|
| Claude Code | `claude` | macOS |
| Codex | `codex` | macOS |
| Kiro CLI on its v3 engine | `kiro-ide` (Kiro IDE and Kiro CLI v3) | macOS |
| Kiro CLI on its V2 engine | `kiro` | macOS |
| opencode 1.19.5 | `opencode` | Linux (Amazon Linux 2023) |

After each install: the compose dropped nothing, every fragment landed, `aidlc doctor` showed no
new problem, the project stayed greenfield, and AI-DLC's source scans were unchanged apart from the
documented exceptions above. After each removal only the project's explicit plugin selection was
left (on Kiro IDE, after the person deletes the compose hook file).

Not tested: the Kiro IDE window itself (its harness was driven through Kiro CLI v3), Windows,
Cursor, GitHub Copilot, OpenCode 2, and the plugins' behaviour across a whole AI-DLC workflow on
every tool.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
