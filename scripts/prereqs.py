# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Render a plugin's install documents for one harness from its need list.

A plugin cannot carry skills or MCP servers, so `<plugin>/prerequisites/requires.json` lists what
the AI installs after the plugin is composed, and `<plugin>/prerequisites/INSTALL.md` says when.
Each zip is built for one harness, so the documents in it can name that harness's paths and
commands outright instead of asking the AI to work them out. This module does that rendering for
`package-plugin.py`:

- `{{SKILLS:<group>}}` on a line of its own becomes the steps that install every skill of that
  group: fetched ones from their repository at a pinned commit, checked against a tree hash;
  bundled ones copied from the zip.
- `{{MCP:<group>}}` becomes the steps that register every MCP server of that group the way this
  harness does it.
- `<!-- harness: kiro-ide kiro -->` ... `<!-- /harness -->` keeps a block only in those harnesses.
- `{{H}}`, `{{S}}`, `{{HARNESS_LABEL}}`, `{{PLUGIN}}`, `{{VERSION}}` are replaced.

requires.json, version 1:

  {"version": 1,
   "skills": [{"name": "...", "group": "...",
               "fetch": {"repo": "https://...", "commit": "<40 hex>", "path": "...", "tree": "<40 hex>"}}
              | {"name": "...", "group": "...", "bundled": "skills/<name>"}],
   "mcp": [{"name": "...", "group": "...", "url": "https://..."}
           | {"name": "...", "group": "...", "url_from": "the URL the person gave in Step 3"}]}
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HARNESS_INFO = {
    "claude": {"H": ".claude", "S": ".claude/skills", "label": "Claude Code"},
    "codex": {"H": ".codex", "S": ".agents/skills", "label": "Codex"},
    "kiro-ide": {"H": ".kiro", "S": ".kiro/skills", "label": "Kiro IDE and Kiro CLI v3"},
    "kiro": {"H": ".kiro", "S": ".kiro/skills", "label": "Kiro CLI V2"},
    "opencode": {"H": ".aidlc", "S": ".aidlc/skills", "label": "opencode"},
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class RenderError(Exception):
    pass


def load(root: Path) -> dict | None:
    path = root / "prerequisites" / "requires.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise RenderError(f"{path}: version must be 1")
    for skill in data.get("skills", []):
        if not NAME.match(skill.get("name", "")) or not skill.get("group"):
            raise RenderError(f"{path}: skill needs a name and a group: {skill}")
        if "fetch" in skill:
            f = skill["fetch"]
            if not f.get("repo", "").startswith("https://") or not f.get("path"):
                raise RenderError(f"{path}: {skill['name']}: fetch needs an https repo and a path")
            if not HEX40.match(f.get("commit", "")) or not HEX40.match(f.get("tree", "")):
                raise RenderError(f"{path}: {skill['name']}: commit and tree must be full 40-hex hashes")
        elif "bundled" in skill:
            if not (root / "prerequisites" / skill["bundled"] / "SKILL.md").is_file():
                raise RenderError(f"{path}: {skill['name']}: no SKILL.md under prerequisites/{skill['bundled']}")
        else:
            raise RenderError(f"{path}: {skill['name']}: needs fetch or bundled")
    for server in data.get("mcp", []):
        if not NAME.match(server.get("name", "")) or not server.get("group"):
            raise RenderError(f"{path}: MCP server needs a name and a group: {server}")
        if bool(server.get("url")) == bool(server.get("url_from")):
            raise RenderError(f"{path}: {server['name']}: give exactly one of url and url_from")
    return data


def bundled_dirs(req: dict | None) -> set[str]:
    return {s["bundled"] for s in (req or {}).get("skills", []) if "bundled" in s}


def _skills_block(req: dict, group: str, harness: str, plugin: str) -> str:
    info = HARNESS_INFO[harness]
    S, H = info["S"], info["H"]
    pre = f"{H}/aidlc-plugins/{plugin}/prerequisites"
    skills = [s for s in req.get("skills", []) if s["group"] == group]
    if not skills:
        raise RenderError(f"{plugin}: no skills in group {group}")
    out: list[str] = []
    for s in [s for s in skills if "bundled" in s]:
        out += [
            f"**`{s['name']}`**, shipped in this folder:",
            "",
            "```bash",
            f'ls "{S}/{s["name"]}" 2>/dev/null && diff -rq "{pre}/{s["bundled"]}" "{S}/{s["name"]}"',
            "```",
            "",
            f"- Not there: `mkdir -p \"{S}\" && cp -R \"{pre}/{s['bundled']}\" \"{S}/{s['name']}\"`.",
            "- There and `diff` prints nothing: the same skill is already present. Move on.",
            "- There and different: show the difference and ask the person before replacing it.",
            "",
        ]
    fetched: dict[tuple[str, str], list[dict]] = {}
    for s in [s for s in skills if "fetch" in s]:
        fetched.setdefault((s["fetch"]["repo"], s["fetch"]["commit"]), []).append(s)
    for (repo, commit), group_skills in fetched.items():
        names = ", ".join(f"`{s['name']}`" for s in group_skills)
        paths = " ".join(s["fetch"]["path"] for s in group_skills)
        out += [
            f"**{names}**, fetched from `{repo}` at commit `{commit[:12]}` (not shipped in this folder):",
            "",
            "```bash",
            'SRC="$(mktemp -d)"        # no argument: the system\'s temporary directory, outside the project',
            f'git clone --quiet --filter=blob:none --no-checkout {repo} "$SRC/repo"',
            f'git -C "$SRC/repo" sparse-checkout set {paths}',
            f'git -C "$SRC/repo" checkout --quiet {commit}',
        ]
        for s in group_skills:
            out.append(f'git -C "$SRC/repo" rev-parse {commit}:{s["fetch"]["path"]}    # expect {s["fetch"]["tree"]}')
        out += [
            "```",
            "",
            "- Every printed hash must equal its `expect` value. One that differs means the content is not",
            "  what this version was measured with: copy nothing from this fetch, and report it.",
            "- `git` is missing or the clone fails: skip these skills, say why, and go on.",
            f"- Your tool cannot write outside the project: use `SRC={H}/aidlc-plugins/{plugin}/.fetch` instead",
            "  (inside the harness directory, which AI-DLC's code scan skips). Never put it anywhere else in",
            "  the project.",
            "",
            "Then, for each of them:",
            "",
            "```bash",
        ]
        for s in group_skills:
            out.append(f'ls "{S}/{s["name"]}" 2>/dev/null && diff -rq "$SRC/repo/{s["fetch"]["path"]}" "{S}/{s["name"]}"')
        out += [
            "```",
            "",
            f"- Not there: `mkdir -p \"{S}\"` once, then `cp -R \"$SRC/repo/<path>\" \"{S}/<name>\"` for each.",
            "- There and `diff` prints nothing: already present. Move on.",
            "- There and different (an older copy is common): show the difference and ask before replacing it.",
            "",
            'Remove the clone when the copies are done: `rm -rf "$SRC"`. If your tool refuses that, leave it',
            "and name the directory in the report for the person to delete.",
            "",
        ]
    if harness == "codex":
        names = [s["name"] for s in skills]
        not_aidlc = [n for n in names if not n.startswith("aidlc")]
        out += [
            "**Keep these skills out of AI-DLC's code scan.** Codex reads skills from the project's",
            "`.agents/skills/`, and AI-DLC's source boundary (what code generation is checked against)",
            "includes that folder. Ask the person once, naming the lines, whether you may add:",
            "",
            "- to `.aidlc-source-paths.json`, under `\"exclude\"`: "
            + ", ".join(f"`\".agents/skills/{n}\"`" for n in names)
            + ". When the file is missing, create it as `{\"version\": 1, \"exclude\": [...]}`. Keep every",
            "  entry already there, and add a line only if it is not there yet.",
        ]
        if not_aidlc:
            out += [
                "- to `.gitignore`: " + ", ".join(f"`/.agents/skills/{n}/`" for n in not_aidlc)
                + ". The CodeKB source snapshot leaves out `.agents/skills/aidlc*` on its own, but not",
                "  these names.",
            ]
        out += [
            "",
            "Add only what the person agrees to, and say in the report what a declined line leaves inside",
            "the scan. Read each file back after the edit.",
            "",
        ]
    out += [
        "For the install record, note each skill: its name, its path, where it came from"
        + " (`<repo>@<commit>` or `bundled`), and whether you installed it or it was already present."
        + (" Note every line you added, too." if harness == "codex" else ""),
    ]
    return "\n".join(out)


def _mcp_block(req: dict, group: str, harness: str, plugin: str) -> str:
    servers = [m for m in req.get("mcp", []) if m["group"] == group]
    if not servers:
        raise RenderError(f"{plugin}: no MCP servers in group {group}")
    out: list[str] = []
    for m in servers:
        n = m["name"]
        url = m.get("url") or f"<{m['url_from']}>"
        if harness == "claude":
            out += [
                f"**`{n}`**, through Claude Code, for this project and this person only:",
                "",
                "```bash",
                f"claude mcp get {n}          # already there with {url} → already present",
                f'claude mcp add --scope local --transport http {n} "{url}"',
                "```",
                "",
                "Do not edit the project's `.mcp.json`: a server there enters AI-DLC's source boundary. An",
                f"`{n}` entry already in `.mcp.json` counts as present; leave it. A `{n}` already",
                "registered with a different URL: show both and ask the person.",
                "",
            ]
        elif harness == "codex":
            out += [
                f"**`{n}`**, in `.codex/config.toml`. Look for `[mcp_servers.{n}]` there and in",
                "`${CODEX_HOME:-$HOME/.codex}/config.toml`. If neither has it, append to `.codex/config.toml`:",
                "",
                "```toml",
                f"[mcp_servers.{n}]",
                f'url = "{url}"',
                "```",
                "",
                "Read the file back (`cat .codex/config.toml`) and check the new table is whole and appears",
                "once. Found with a different URL: show both and ask the person.",
                "",
            ]
        elif harness == "opencode":
            out += [
                f"**`{n}`**, in the project-root `opencode.json` (or `opencode.jsonc`), under `\"mcp\"`. First",
                f"look for `{n}` there and in `~/.config/opencode/opencode.json` (`cat` each; a missing",
                f"person file is fine). A `{n}` in the person's file already reaches this project: say so and",
                "add no second one. Otherwise add this one key with your file tool, creating `\"mcp\"` if the",
                "file has none, and change nothing else:",
                "",
                "```json",
                f'"{n}": {{"type": "remote", "url": "{url}"}}',
                "```",
                "",
                "Read the file back (still valid JSON, AI-DLC's own keys as they were), then check that",
                "opencode reads it:",
                "",
                "```bash",
                f"opencode mcp list        # lists {n}; before its login it may show as failed or needing auth",
                "```",
                "",
                "Found with a different URL: show both and ask the person.",
                "",
            ]
        else:
            out += [
                f"**`{n}`**, in `.kiro/settings/mcp.json`. First look in `.kiro/settings/mcp.json` and",
                f"`~/.kiro/settings/mcp.json` (`cat` each; a missing file is fine). A `{n}` in the person's",
                "`~/.kiro/settings/mcp.json` already reaches this project: say so and add no second one.",
                "Otherwise add it through Kiro's own command:",
                "",
                "```bash",
                f'kiro-cli mcp add --name {n} --url "{url}" --scope workspace',
                "cat .kiro/settings/mcp.json",
                "```",
                "",
                "Kiro CLI on its v3 engine refuses a direct file write to `.kiro/settings/mcp.json`",
                "(`Blocked by a permission rule … Source: kiro-scope`). That is deliberate: do not get around",
                "it with another tool.",
            ]
            if harness == "kiro-ide":
                out += [
                    "Without `kiro-cli` (Kiro IDE only): read the file; create it as `{\"mcpServers\": {}}` if it",
                    "is missing; add the one key and change nothing else. If the write is refused, show the",
                    "person the key and ask them to add it through Kiro IDE's \"Open workspace MCP config\".",
                ]
            out += [
                "",
                "Read the file back: still valid JSON, the other entries as they were (a reorder by",
                "`kiro-cli` is fine), including any `\"disabled\": true` on stock servers. Found with a",
                "different URL: show both and ask the person.",
                "",
            ]
    where = {
        "claude": None,
        "codex": "`.codex/config.toml`",
        "kiro-ide": "`.kiro/settings/mcp.json`",
        "kiro": "`.kiro/settings/mcp.json`",
        "opencode": "`opencode.json`",
    }[harness]
    if where:
        out += [
            f"{where} is a project file. Tell the person: committing it shares the server URL with everyone",
            "who clones the project; a server meant for one person belongs in "
            + {"codex": "`${CODEX_HOME:-$HOME/.codex}/config.toml`.",
               "opencode": "`~/.config/opencode/opencode.json`."}.get(harness, "`~/.kiro/settings/mcp.json`."),
            "",
        ]
    names = [m["name"] for m in servers]
    if harness == "kiro-ide":
        out += [
            "AI-DLC's agents see the server on their own: every AI-DLC agent file sets",
            "`includeMcpJson: true`. Never edit `.kiro/agents/aidlc*`. Check:",
            "",
            "```bash",
            "grep -c '^includeMcpJson: true' .kiro/agents/aidlc*.md       # one per file",
            "```",
            "",
        ]
    elif harness == "opencode":
        out += [
            "AI-DLC's opencode agents see the server on their own: their agent files restrict only the",
            "`task` tool. Never edit `.opencode/agents/aidlc*`.",
            "",
        ]
    elif harness == "kiro":
        out += [
            "Then let AI-DLC's agents see it. On Kiro CLI V2, `aidlc config` writes `\"@<server>\"` into every",
            "AI-DLC agent JSON for each server in `mcp.json`. Run it once, after the servers above:",
            "",
            "```bash",
            'aidlc config --project-dir "<project>"',
        ]
        out += [f"grep -l '\"@{n}\"' .kiro/agents/*.json        # every agent JSON" for n in names]
        out += [
            "```",
            "",
            "If it reports conflicts, show them and stop. Never pass `--force`, and never edit",
            "`.kiro/agents/aidlc*` yourself.",
            "",
        ]
    out += [
        "For the install record, note each server: its name, where it went (the file, or `claude mcp,"
        + " local scope`), and whether you added it or it was already present.",
    ]
    return "\n".join(out)


HARNESS_BLOCK = re.compile(r"<!-- harness: ([a-z -]+) -->\n(.*?)<!-- /harness -->\n?", re.S)
DIRECTIVE = re.compile(r"^\{\{(SKILLS|MCP):([a-z0-9-]+)\}\}$", re.M)


def render(text: str, req: dict | None, harness: str, plugin: str, version: str) -> str:
    def keep(m: re.Match) -> str:
        wanted = m.group(1).split()
        unknown = [h for h in wanted if h not in HARNESS_INFO]
        if unknown:
            raise RenderError(f"{plugin}: unknown harness in block: {unknown}")
        return m.group(2) if harness in wanted else ""

    text = HARNESS_BLOCK.sub(keep, text)

    def expand(m: re.Match) -> str:
        if req is None:
            raise RenderError(f"{plugin}: {m.group(0)} but no prerequisites/requires.json")
        kind, group = m.group(1), m.group(2)
        return (_skills_block if kind == "SKILLS" else _mcp_block)(req, group, harness, plugin)

    text = DIRECTIVE.sub(expand, text)
    info = HARNESS_INFO[harness]
    for key, value in {"H": info["H"], "S": info["S"], "HARNESS_LABEL": info["label"],
                       "PLUGIN": plugin, "VERSION": version}.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{" in text or "<!-- harness" in text or "<!-- /harness" in text:
        left = re.findall(r"\{\{[^}]*\}\}|<!-- /?harness[^>]*-->", text)
        raise RenderError(f"{plugin}: unrendered markers left for {harness}: {sorted(set(left))}")
    return text


def agent_names(root: Path) -> list[str]:
    """The plugin's own agents; on opencode compose writes each to `.opencode/agents/<name>.md`."""
    return sorted(p.stem for p in (root / "agents").glob("*.md")) if (root / "agents").is_dir() else []


def runner_names(root: Path) -> list[str]:
    """The runner skills AI-DLC generates for a plugin's own stages and scopes (one per slug)."""
    names = [p.stem for p in (root / "stages").rglob("*.md")] if (root / "stages").is_dir() else []
    names += [p.stem for p in (root / "scopes").glob("*.md")] if (root / "scopes").is_dir() else []
    return sorted(names)
