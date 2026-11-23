# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""Package a plugin as one zip per harness, each unzipped at an AI-DLC project's root.

WHY THIS EXISTS. AI-DLC has no command a person types to install a plugin. A zip that lands the
plugin inside the harness directory, plus an INSTALL.md the AI follows, works the same way on every
tool: unzip, then one prompt. Where the plugin may sit was measured, not chosen: anything outside
the harness directory can turn a new project brownfield or enter the reverse-engineering scan
(see README, "Distribute").

  aidlc-<p>-<v>-claude.zip    .claude/aidlc-plugins/<p>/
  aidlc-<p>-<v>-codex.zip     .codex/aidlc-plugins/<p>/
  aidlc-<p>-<v>-kiro-ide.zip  .kiro/aidlc-plugins/<p>/  + .kiro/hooks/aidlc-<p>-compose.json
  aidlc-<p>-<v>-kiro.zip      .kiro/aidlc-plugins/<p>/
  aidlc-<p>-<v>-opencode.zip  .aidlc/aidlc-plugins/<p>/   (opencode's engine directory is .aidlc/)

Each plugin folder holds the builder's projection, the plugin's `prerequisites/`, an INSTALL.md
made from `install/<claude-code|codex|kiro|opencode>.md` and a REMOVE.md made from
`install/remove-<claude-code|codex|kiro|opencode>.md`. Every document is rendered for the zip's harness from
the plugin's `prerequisites/requires.json` (`scripts/prereqs.py`). The builder reads neither
`prerequisites/` nor `install/`, so this script adds them.

usage: package-plugin.py --tools <dir with aidlc-plugin-build.ts> --out <dir>
                         [--harness claude,codex,kiro-ide,kiro,opencode] [--plain-name] <plugin-root>...

--plain-name drops the harness from the file name (`aidlc-<p>-<v>.zip`) for a distribution that
ships one harness only; it needs exactly one --harness.
"""
from __future__ import annotations

import json
import shutil
import subprocess  # nosec B404 - runs only bun with argument lists; see bun()
import sys
import tempfile
import zipfile
from pathlib import Path

import prereqs

REPO = Path(__file__).resolve().parent.parent
HARNESSES = ("claude", "codex", "kiro-ide", "kiro", "opencode")
# harness → (harness directory, install template, product name for the template)
TARGETS = {
    "claude": (".claude", "claude-code.md", "Claude Code"),
    "codex": (".codex", "codex.md", "Codex"),
    "kiro-ide": (".kiro", "kiro.md", "Kiro IDE and Kiro CLI v3"),
    "kiro": (".kiro", "kiro.md", "Kiro CLI V2"),
    "opencode": (".aidlc", "opencode.md", "opencode"),
}
REMOVE_TEMPLATES = {"claude": "remove-claude-code.md", "codex": "remove-codex.md",
                    "kiro-ide": "remove-kiro.md", "kiro": "remove-kiro.md",
                    "opencode": "remove-opencode.md"}


def manifest(root: Path) -> tuple[str, str]:
    data = json.loads((root / ".aidlc-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return data["name"], data["version"]


def bun(args: list[str]) -> subprocess.CompletedProcess:
    """Run bun on an AI-DLC plugin tool. The only place this script starts a process.

    No shell: the command is an argument list, and its first element is bun's absolute path. Every
    other argument is a fixed tool file name under --tools, a path this script resolved itself, or a
    harness id checked against TARGETS, so no part of it is taken from untrusted input.
    """
    exe = shutil.which("bun")
    if not exe:
        sys.exit("bun not found on PATH: the plugin tools run with bun")
    argv = [exe, *args]
    return subprocess.run(argv, capture_output=True, text=True, shell=False)  # nosemgrep  # nosec B603


def run(args: list[str]) -> None:
    done = bun(args)
    if done.returncode != 0:
        sys.exit(f"failed: bun {' '.join(args)}\n{done.stdout}{done.stderr}")


def build(tools: Path, root: Path, harness: str, out: Path) -> None:
    """Run the builder of `tools` for one harness id (the id a project's harness.json records).

    From 2.11.4 the builder takes the name a person types: `kiro` builds Kiro (id `kiro-ide`) and
    Kiro CLI V2 is `kiro-v2` (upstream #2924). Earlier builders know only `kiro` for V2 and refuse
    `kiro-v2`, so the V2 build asks for `kiro-v2` first and falls back to `kiro` on that refusal.
    """
    if harness not in TARGETS:
        sys.exit(f"unknown harness: {harness}")
    cmd = [str(tools / "aidlc-plugin-build.ts"), str(root), harness, str(out)]
    if harness == "kiro":
        cmd[2] = "kiro-v2"
        done = bun(cmd)
        if done.returncode == 0:
            return
        if 'Unknown harness "kiro-v2"' not in done.stdout + done.stderr:
            sys.exit(f"failed: bun {' '.join(cmd)}\n{done.stdout}{done.stderr}")
        shutil.rmtree(out, ignore_errors=True)
        cmd[2] = "kiro"
    run(cmd)


def zip_name(name: str, version: str, harness: str, plain: bool) -> str:
    return f"aidlc-{name}-{version}.zip" if plain else f"aidlc-{name}-{version}-{harness}.zip"


def runner_excludes(root: Path) -> str:
    """Codex only: the runner skills sync writes into `.agents/skills/` for the plugin's stages."""
    names = prereqs.runner_names(root)
    if not names:
        return "This plugin adds no stages or scopes: nothing to do here.\n"
    lines = ", ".join(f'`".agents/skills/{n}"`' for n in names)
    return (
        "This plugin adds stages or scopes, so sync also wrote their runner skills into the project's\n"
        "`.agents/skills/` (" + ", ".join(f"`{n}`" for n in names) + "). AI-DLC's own runners sit there\n"
        "too, and its source boundary includes them; the CodeKB snapshot already leaves runners out.\n"
        "Ask the person whether you may add to `.aidlc-source-paths.json`, under `\"exclude\"`: " + lines + ".\n"
        "Create the file as `{\"version\": 1, \"exclude\": [...]}` when it is missing, keep every entry\n"
        "already there, and read it back. Note each added line for the install record.\n"
    )


def persona_excludes(root: Path) -> str:
    """opencode only: compose writes the plugin's agents to `.opencode/agents/`, inside the source boundary."""
    names = prereqs.agent_names(root)
    if not names:
        return "This plugin adds no agents: nothing to do here.\n"
    lines = ", ".join(f'`".opencode/agents/{n}.md"`' for n in names)
    return (
        "This plugin adds agents, so sync also wrote them into `.opencode/agents/` ("
        + ", ".join(f"`{n}.md`" for n in names) + "), where opencode\n"
        "finds subagents. AI-DLC's source boundary (what code generation is checked against) includes\n"
        "that file; the CodeKB snapshot does not. Ask the person whether you may add to\n"
        "`.aidlc-source-paths.json`, under `\"exclude\"`: " + lines + ".\n"
        "Create the file as `{\"version\": 1, \"exclude\": [...]}` when it is missing, keep every entry\n"
        "already there, add a line only if it is not there yet, and read it back. Note each added line\n"
        "for the install record. On a no, say in the report that the agent file stays inside the scan.\n"
    )


def requires_summary(req: dict | None, harness: str, root: Path) -> str:
    """One line naming what the install may have put into the project besides AI-DLC's own files."""
    S = prereqs.HARNESS_INFO[harness]["S"]
    parts = [f"the skill folder `{S}/{s['name']}`" for s in (req or {}).get("skills", [])]
    parts += [f"the MCP server `{m['name']}`" for m in (req or {}).get("mcp", [])]
    if harness == "codex":
        names = [s["name"] for s in (req or {}).get("skills", [])] + prereqs.runner_names(root)
        if names:
            parts.append("`.aidlc-source-paths.json` exclude entries (and `.gitignore` lines) for "
                         + ", ".join(f"`.agents/skills/{n}`" for n in names))
    if harness == "opencode" and prereqs.agent_names(root):
        parts.append("`.aidlc-source-paths.json` exclude entries for "
                     + ", ".join(f"`.opencode/agents/{n}.md`" for n in prereqs.agent_names(root)))
    return "; ".join(parts) if parts else "nothing (it has no skills, servers or added lines)"


def render_doc(template: str, root: Path, harness: str, name: str, version: str, zip_file: str,
               req: dict | None) -> str:
    product = TARGETS[harness][2]
    text = (REPO / "install" / template).read_text(encoding="utf-8")
    values = {"HARNESS": harness, "PRODUCT": product, "ZIP": zip_file,
              "RUNNER_EXCLUDES": runner_excludes(root) if harness == "codex" else "",
              "PERSONA_EXCLUDES": persona_excludes(root) if harness == "opencode" else "",
              "REQUIRES_SUMMARY": requires_summary(req, harness, root)}
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    try:
        return prereqs.render(text, req, harness, name, version)
    except prereqs.RenderError as error:
        sys.exit(f"install/{template}: {error}")


def stage(root: Path, harness: str, tools: Path, work: Path, zip_file: str) -> Path:
    """Build the projection and lay it out as it must land under the project root."""
    name, version = manifest(root)
    hd = TARGETS[harness][0]
    built = work / f"build-{harness}"
    build(tools, root, harness, built)
    tree = work / f"tree-{harness}"
    if harness.startswith("kiro"):
        # The Kiro projection already is `.kiro/aidlc-plugins/<p>/` (+ `.kiro/hooks/` for the IDE).
        # Check which Kiro it was built for: a Kiro IDE hook in a V2 zip, or none in a Kiro zip,
        # means the builder read the harness name differently from this script.
        hook = built / ".kiro" / "hooks" / f"aidlc-{name}-compose.json"
        if harness == "kiro-ide" and not hook.is_file():
            sys.exit(f"kiro-ide: projection has no .kiro/hooks/{hook.name}: not a Kiro IDE build")
        if harness == "kiro" and (built / ".kiro" / "hooks").exists():
            sys.exit("kiro: projection has .kiro/hooks/: a Kiro IDE build, not Kiro CLI V2")
        shutil.copytree(built / ".kiro", tree / ".kiro")
    else:
        shutil.copytree(built, tree / hd / "aidlc-plugins" / name)
    folder = tree / hd / "aidlc-plugins" / name
    if not (folder / ".aidlc-plugin" / "plugin.json").is_file():
        sys.exit(f"{harness}: projection has no {hd}/aidlc-plugins/{name}/.aidlc-plugin/plugin.json")
    try:
        req = prereqs.load(root)
    except prereqs.RenderError as error:
        sys.exit(str(error))
    if (root / "prerequisites").is_dir():
        shutil.copytree(root / "prerequisites", folder / "prerequisites")
        pre_doc = folder / "prerequisites" / "INSTALL.md"
        if pre_doc.is_file():
            try:
                pre_doc.write_text(prereqs.render(pre_doc.read_text(encoding="utf-8"), req, harness, name, version),
                                   encoding="utf-8")
            except prereqs.RenderError as error:
                sys.exit(f"{name}/prerequisites/INSTALL.md: {error}")
        skills_dir = folder / "prerequisites" / "skills"
        if skills_dir.is_dir():
            shipped = {f"skills/{p.name}" for p in skills_dir.iterdir() if p.is_dir()}
            unlisted = shipped - prereqs.bundled_dirs(req)
            if unlisted:
                sys.exit(f"{name}: prerequisites ships {sorted(unlisted)} but requires.json does not list them")
    (folder / "INSTALL.md").write_text(
        render_doc(TARGETS[harness][1], root, harness, name, version, zip_file, req), encoding="utf-8")
    (folder / "REMOVE.md").write_text(
        render_doc(REMOVE_TEMPLATES[harness], root, harness, name, version, zip_file, req), encoding="utf-8")
    return tree


def write_zip(tree: Path, target: Path) -> int:
    files = sorted(p for p in tree.rglob("*") if p.is_file() and p.name != ".DS_Store")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(tree).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes())
    return len(files)


def main() -> int:
    args = sys.argv[1:]

    def take(flag: str) -> str | None:
        if flag not in args:
            return None
        i = args.index(flag)
        value = args[i + 1]
        del args[i : i + 2]
        return value

    tools, out, harness_arg = take("--tools"), take("--out"), take("--harness")
    plain = "--plain-name" in args
    if plain:
        args.remove("--plain-name")
    if not tools or not out or not args:
        sys.exit((__doc__ or "").split("usage: ", 1)[-1])
    tools_dir, out_dir = Path(tools).resolve(), Path(out).resolve()
    harnesses = harness_arg.split(",") if harness_arg else list(HARNESSES)
    unknown = [h for h in harnesses if h not in TARGETS]
    if unknown:
        sys.exit(f"unknown harness: {', '.join(unknown)}")
    if plain and len(harnesses) != 1:
        sys.exit("--plain-name needs exactly one --harness: the zip name no longer says which")
    if not (tools_dir / "aidlc-plugin-build.ts").is_file():
        sys.exit(f"no aidlc-plugin-build.ts in {tools_dir}")
    roots = [Path(a).resolve() for a in args]
    for root in roots:
        if out_dir == root or root in out_dir.parents:
            sys.exit(f"--out must be outside the plugin source: {root}")
    out_dir.mkdir(parents=True, exist_ok=True)

    for root in roots:
        name, version = manifest(root)
        run([str(tools_dir / "aidlc-plugin-validate.ts"), str(root)])
        with tempfile.TemporaryDirectory(prefix=f"pkg-{name}-") as tmp:
            for harness in harnesses:
                target = out_dir / zip_name(name, version, harness, plain)
                tree = stage(root, harness, tools_dir, Path(tmp), target.name)
                count = write_zip(tree, target)
                print(f"{target.name}  {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
