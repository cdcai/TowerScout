#!/usr/bin/env python3
"""Build and validate an offline TowerScout documentation review ZIP."""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import zipfile

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_URL = "https://github.com/J-Schulein/TowerScout"
PR_URL = f"{REPOSITORY_URL}/pull/94"

WIKI_SOURCES = {
    "Home.md": "Home / Start Here",
    "Before-You-Install.md": "Before You Install",
    "Choose-Your-Setup.md": "Choose Your Setup",
    "Install-And-First-Run.md": "Install And First Run",
    "Google-And-Azure-API-Credentials.md": "Google And Azure API Credentials",
    "Everyday-Commands.md": "Everyday Commands",
    "Docker-Guidance.md": "Docker Guidance",
    "Podman-Guidance.md": "Podman Guidance",
    "NVIDIA-GPU-Setup.md": "NVIDIA GPU Setup",
    "Troubleshooting-And-Safe-Support.md": "Troubleshooting And Safe Support",
    "Local-IT-Administrator-Guide.md": "Local IT Administrator Guide",
    "Demo-Video-And-Written-Walkthrough.md": "Demo Video And Written Walkthrough",
    "Releases-And-Supported-Versions.md": "Releases And Supported Versions",
    "Licensing-Privacy-And-Provider-Terms.md": "Licensing, Privacy, And Provider Terms",
    "_Sidebar.md": "Wiki Sidebar",
}

DOC_SOURCES = {
    "README.md": ("Repository-README.html", "Repository README"),
    "docs/project-overview.md": ("project-overview.html", "Project Overview"),
    "docs/quick-start.md": ("quick-start.html", "Quick Start"),
    "docs/user-guide.md": ("user-guide.html", "User Guide"),
    "docs/local-it-administrator-guide.md": (
        "local-it-administrator-guide.html",
        "Local IT Administrator Guide",
    ),
    "docs/package-guide.md": ("package-guide.html", "Package Guide"),
    "docs/docker-cpu-user-guide.md": (
        "docker-cpu-user-guide.html",
        "Docker CPU User Guide",
    ),
    "docs/docker-gpu-user-guide.md": (
        "docker-gpu-user-guide.html",
        "Docker GPU User Guide",
    ),
    "docs/podman-cpu-user-guide.md": (
        "podman-cpu-user-guide.html",
        "Podman CPU User Guide",
    ),
    "docs/podman-gpu-user-guide.md": (
        "podman-gpu-user-guide.html",
        "Podman GPU User Guide",
    ),
    "docs/support/oci-quick-start.md": ("oci-quick-start.html", "OCI Quick Start"),
    "docs/support/oci-runtime-contract.md": (
        "oci-runtime-contract.html",
        "OCI Runtime Contract",
    ),
    "docs/support/host-helper.md": (
        "host-helper.html",
        "Deferred Host Helper Reference",
    ),
}

MAINTAINED_HTML = (
    "project-overview.html",
    "quick-start.html",
    "user-guide.html",
    "local-it-administrator-guide.html",
)

REVIEW_CSS = """:root {
  color-scheme: light;
  --background: #f4f7fa;
  --panel: #ffffff;
  --text: #202b33;
  --muted: #52616b;
  --border: #cbd5df;
  --accent: #0f766e;
  --accent-dark: #115e59;
  --code: #edf3f7;
  --warning: #fff8db;
}
* { box-sizing: border-box; }
body { margin: 0; color: var(--text); background: var(--background); font-family: Arial, Helvetica, sans-serif; font-size: 17px; line-height: 1.62; }
a { color: var(--accent-dark); text-underline-offset: 0.16em; }
.review-header { padding: 2.25rem max(1.25rem, calc((100% - 980px) / 2)); color: white; background: #0f172a; }
.review-header h1 { max-width: 980px; margin: 0.25rem 0; }
.review-header p { max-width: 900px; margin: 0.5rem 0 0; }
.eyebrow { color: #a7f3d0; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; }
.review-toolbar { display: flex; gap: 1.25rem; padding: 0.85rem max(1.25rem, calc((100% - 980px) / 2)); border-bottom: 1px solid var(--border); background: white; }
.review-index, .review-page { width: min(980px, calc(100% - 2rem)); margin: 1.5rem auto 3rem; }
.review-index section, .markdown-body, .review-metadata { margin-bottom: 1.25rem; padding: 1.25rem 1.5rem; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }
.review-callout, .review-metadata { border-left: 5px solid var(--accent); }
.review-metadata { color: var(--muted); font-size: 0.92rem; }
h1, h2, h3, h4 { line-height: 1.25; }
h2 { margin-top: 2rem; padding-bottom: 0.35rem; border-bottom: 1px solid var(--border); }
h3 { margin-top: 1.7rem; }
p, li { max-width: 82ch; }
li + li { margin-top: 0.3rem; }
code, pre { font-family: Consolas, "Courier New", monospace; }
code { padding: 0.08rem 0.3rem; border-radius: 4px; background: var(--code); }
pre { overflow-x: auto; padding: 1rem; border-radius: 7px; background: var(--code); }
pre code { padding: 0; background: transparent; }
blockquote { margin: 1rem 0; padding: 0.8rem 1rem; border-left: 5px solid #b7791f; background: var(--warning); }
table { display: block; width: 100%; overflow-x: auto; border-collapse: collapse; }
th, td { padding: 0.65rem; border: 1px solid var(--border); text-align: left; vertical-align: top; }
th { background: var(--code); }
.button { display: inline-block; padding: 0.55rem 0.85rem; border-radius: 6px; color: white; background: var(--accent-dark); font-weight: 700; text-decoration: none; }
.review-skip { position: absolute; left: -9999px; top: 0; z-index: 1000; padding: 0.65rem 0.85rem; color: white; background: #111827; }
.review-skip:focus { left: 0.75rem; top: 0.75rem; }
a:focus-visible { outline: 3px solid #f59e0b; outline-offset: 3px; }
.review-change-list { border-left: 5px solid #2563eb; }
@media (max-width: 680px) {
  body { font-size: 16px; }
  .review-header { padding-top: 1.5rem; padding-bottom: 1.5rem; }
  .review-toolbar { flex-direction: column; gap: 0.35rem; }
  .review-index section, .markdown-body, .review-metadata { padding: 1rem; }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--name", default="TowerScout-Documentation-Review-v5-2026-10-05")
    parser.add_argument("--branch", default="docs/pre-rc4-checkpoint-2026-10-02")
    parser.add_argument(
        "--instructions",
        default=".agent_work/tasks/active/TASK-092/REVIEWER-INSTRUCTIONS-ROUND-5-2026-10-05.md",
    )
    parser.add_argument("--output-root", default="dist/review")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def heading_ids(rendered: str) -> str:
    counts: dict[str, int] = {}

    def add_id(match: re.Match[str]) -> str:
        level, body = match.groups()
        plain = html.unescape(re.sub(r"<[^>]+>", "", body)).strip().lower()
        slug = re.sub(r"[^\w\- ]", "", plain, flags=re.UNICODE)
        slug = re.sub(r"[\s\-]+", "-", slug).strip("-") or "section"
        occurrence = counts.get(slug, 0)
        counts[slug] = occurrence + 1
        if occurrence:
            slug = f"{slug}-{occurrence}"
        return f'<h{level} id="{html.escape(slug, quote=True)}">{body}</h{level}>'

    return re.sub(r"<h([1-6])>(.*?)</h\1>", add_id, rendered, flags=re.DOTALL)


def rewrite_markdown_links(text: str, source: Path, group: str, commit: str) -> str:
    doc_outputs = {key: value[0] for key, value in DOC_SOURCES.items()}
    wiki_outputs = {name: f"{Path(name).stem}.html" for name in WIKI_SOURCES}

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        target = target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            return match.group(0)

        parts = urlsplit(target)
        target_path = unquote(parts.path)
        replacement: str | None = None

        if group == "wiki":
            candidate = target_path
            if candidate.endswith(".md"):
                candidate = candidate[:-3]
            candidate_name = f"{Path(candidate).name}.md"
            if candidate_name in wiki_outputs:
                replacement = wiki_outputs[candidate_name]
        else:
            candidate = (source.parent / target_path).resolve()
            try:
                candidate_relative = repository_path(candidate)
            except ValueError:
                candidate_relative = ""
            if candidate_relative in doc_outputs:
                replacement = doc_outputs[candidate_relative]
            elif candidate.is_file() and candidate_relative:
                replacement = f"{REPOSITORY_URL}/blob/{commit}/{candidate_relative}"

        if replacement is None:
            return match.group(0)
        if parts.fragment:
            replacement += f"#{parts.fragment}"
        return f"{prefix}{replacement}{suffix}"

    return re.sub(r"(!?\[[^\]]*\]\()([^\s)]+)([^)]*\))", replace, text)


def render_markdown(text: str) -> str:
    renderer = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    return heading_ids(renderer.render(text))


def document_wrapper(
    title: str, source: str, commit: str, body: str, prefix: str = "../"
) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} — TowerScout documentation review v5</title>
  <link rel="stylesheet" href="{prefix}assets/review.css">
</head>
<body>
  <a class="review-skip" href="#review-content">Skip to reviewed document</a>
  <header class="review-header">
    <p class="eyebrow">TowerScout documentation review v5</p>
    <h1>{safe_title}</h1>
    <p>Review only — not a release package and not final release approval.</p>
  </header>
  <div class="review-toolbar">
    <a href="{prefix}index.html">Review index</a>
    <a href="{prefix}reviewer-instructions.html">Reviewer instructions</a>
  </div>
  <main class="review-page" id="review-content">
    <aside class="review-metadata">
      <strong>Source:</strong> {html.escape(source)}<br>
      <strong>Source commit:</strong> <code>{html.escape(commit)}</code>
    </aside>
    <article class="markdown-body">
{body}
    </article>
  </main>
</body>
</html>
"""


def rewrite_maintained_links(text: str, source: Path, commit: str) -> str:
    doc_outputs = {key: value[0] for key, value in DOC_SOURCES.items()}

    def replace(match: re.Match[str]) -> str:
        quote, target = match.groups()
        if target.startswith(("#", "http://", "https://", "mailto:")):
            return match.group(0)
        parts = urlsplit(target)
        candidate = (source.parent / unquote(parts.path)).resolve()
        try:
            relative = repository_path(candidate)
        except ValueError:
            return match.group(0)
        if relative in doc_outputs:
            replacement = f"../rendered-docs/{doc_outputs[relative]}"
        elif candidate.is_file() and candidate.suffix.lower() != ".css":
            replacement = f"{REPOSITORY_URL}/blob/{commit}/{relative}"
        else:
            return match.group(0)
        if parts.fragment:
            replacement += f"#{parts.fragment}"
        return f"href={quote}{replacement}{quote}"

    return re.sub(r"href=([\"'])([^\"']+)\1", replace, text)


def route_note() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Running-application route note</title>
  <link rel="stylesheet" href="towerscout-docs.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to route note</a>
  <header class="page-header">
    <p class="eyebrow">TowerScout documentation review v5</p>
    <h1>Running-Application Route Note</h1>
    <p class="lead">This offline review bundle cannot open routes served only by a running TowerScout container.</p>
  </header>
  <div class="doc-frame"><main class="doc-main" id="main-content">
    <section class="doc-section" id="license"><h2>Formatted License Route</h2><p>The running application exposes a formatted source and license route at <code>/license</code>. It will be checked from the exact documentation-aligned image after the rebuild.</p></section>
    <section class="doc-section" id="license-txt"><h2>Plain-Text License Route</h2><p>The running application exposes plain-text combined notices at <code>/license.txt</code>. It will be checked from the exact documentation-aligned image after the rebuild.</p></section>
  </main></div>
</body>
</html>
"""


def index_html(commit: str, branch: str) -> str:
    journey = (
        "Home.md",
        "Before-You-Install.md",
        "Choose-Your-Setup.md",
        "Google-And-Azure-API-Credentials.md",
        "Install-And-First-Run.md",
        "Everyday-Commands.md",
        "Troubleshooting-And-Safe-Support.md",
    )
    journey_items = "\n".join(
        f'<li><a href="rendered-wiki/{Path(name).stem}.html">{html.escape(WIKI_SOURCES[name])}</a></li>'
        for name in journey
    )
    remaining_items = "\n".join(
        f'<li><a href="rendered-wiki/{Path(name).stem}.html">{html.escape(title)}</a></li>'
        for name, title in WIKI_SOURCES.items()
        if name not in journey
    )
    docs_items = "\n".join(
        f'<li><a href="rendered-docs/{output}">{html.escape(title)}</a></li>'
        for output, title in DOC_SOURCES.values()
    )
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>TowerScout documentation review v5</title><link rel="stylesheet" href="assets/review.css"></head>
<body>
  <a class="review-skip" href="#review-content">Skip to review index</a>
  <header class="review-header"><p class="eyebrow">TowerScout documentation review v5</p><h1>Start Here</h1><p>Final one-finding confirmation before documentation content freeze and rebuild.</p></header>
  <main class="review-index" id="review-content">
    <section class="review-callout"><h2>Review boundary</h2><p>This ZIP is not a TowerScout release package. It contains no application binaries, model/data assets, provider credentials, logs, browser-run evidence, or release images.</p><p><strong>Branch:</strong> <code>{html.escape(branch)}</code><br><strong>Source commit:</strong> <code>{html.escape(commit)}</code><br><strong>Draft PR:</strong> <a href="{PR_URL}">J-Schulein/TowerScout #94</a></p><p><a class="button" href="reviewer-instructions.html">Open Round 5 Reviewer Instructions</a></p></section>
    <section class="review-change-list"><h2>Round 5 focus</h2><p>Confirm the packaged OCI Runtime Contract no longer tells readers to pass <code>-Port</code> to <code>logs.cmd</code>, accurately names the commands that preserve the selected port, and retains a clear Local IT next action. No broad documentation review is requested.</p></section>
    <section><h2>Pass 1: complete new-user Wiki journey</h2><ol>{journey_items}</ol></section>
    <section><h2>Pass 2: remaining rendered Wiki pages</h2><ul>{remaining_items}</ul></section>
    <section><h2>Pass 3: rendered package and repository Markdown</h2><ul>{docs_items}</ul></section>
    <section><h2>Maintained HTML for packaged and in-app review</h2><ul><li><a href="maintained-html/project-overview.html">Project Overview</a></li><li><a href="maintained-html/quick-start.html">Quick Start — required 1440/720 regression check</a></li><li><a href="maintained-html/user-guide.html">User Guide</a></li><li><a href="maintained-html/local-it-administrator-guide.html">Local IT Administrator Guide</a></li><li><a href="maintained-html/app-route-note.html">Running-application route note</a></li></ul></section>
    <section><h2>Bundle identity</h2><ul><li><a href="REVIEWER-INSTRUCTIONS.md">Reviewer Instructions (Markdown)</a></li><li><a href="SOURCE.txt">Source, scope, and evidence record</a></li><li><a href="SHA256SUMS.txt">Internal file checksums</a></li></ul></section>
  </main>
</body>
</html>
"""


def source_record(commit: str, branch: str) -> str:
    return f"""TowerScout documentation review bundle v5

Purpose: Final one-finding confirmation of the Round 4 OCI port-guidance
correction before documentation content freeze and rebuild. This is not a
TowerScout release package and contains no application binaries, container
images, model/data assets, provider credentials, logs, raw browser-run
evidence, or investigation data.

Generated: 2026-10-05 (America/New_York)
Repository: {REPOSITORY_URL}
Draft PR: {PR_URL}
Branch: {branch}
Source commit: {commit}

Included:
- 15 rendered current Wiki sources
- 13 rendered current repository/package Markdown sources
- Four current manually maintained HTML guides and their stylesheet
- An offline running-application route note
- Round 5 Reviewer Instructions in HTML and Markdown
- Internal SHA-256 inventory

Offline-only transformations:
- Included local Markdown/Wiki links point to rendered HTML counterparts.
- Other repository-local links point to the identified source commit.
- Maintained HTML links to included Markdown point to rendered review copies.
- No user-facing source content was otherwise rewritten for this bundle.

Supplemental Round 4 evidence intentionally not included:
- TowerScout-Round-4-Focused-Review-2026-10-05.md, SHA-256
  5d66b0b2ffd0a7cb09f622943d5b0d89dfca0b9e0f40bc68e44a989eb5de9985
- oci-port-recovery-720.png, SHA-256
  1f0c6303e0142b50f31b2b048256ba2efe64caa2a53eb1bad7df48762a409ce7

Excluded:
- Historical pilot/compatibility pages
- Internal planning other than this source/scope record
- External review reports and supplemental screenshots
- Release binaries, images, manifests, model/data assets, evidence, and secrets
"""


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "link" and values.get("href"):
            self.hrefs.append(values["href"] or "")


def validate_links(bundle: Path) -> tuple[int, int]:
    html_files = sorted(bundle.rglob("*.html"))
    parsed: dict[Path, LinkCollector] = {}
    for page in html_files:
        collector = LinkCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = collector

    errors: list[str] = []
    checked = 0
    for page, collector in parsed.items():
        for href in collector.hrefs:
            parts = urlsplit(href)
            if parts.scheme or href.startswith(("mailto:", "//")):
                continue
            target = page if not parts.path else (page.parent / unquote(parts.path)).resolve()
            try:
                target.relative_to(bundle.resolve())
            except ValueError:
                errors.append(f"{page.name}: link escapes bundle: {href}")
                continue
            checked += 1
            if not target.is_file():
                errors.append(f"{page.relative_to(bundle)}: missing {href}")
                continue
            if parts.fragment and target.suffix.lower() == ".html":
                target_collector = parsed.get(target)
                if target_collector and parts.fragment not in target_collector.ids:
                    errors.append(
                        f"{page.relative_to(bundle)}: missing fragment {href}"
                    )
    if errors:
        raise RuntimeError("Local-link validation failed:\n" + "\n".join(errors[:30]))
    return len(html_files), checked


def main() -> int:
    args = parse_args()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if head != args.source_commit:
        raise RuntimeError(f"HEAD {head} does not match --source-commit {args.source_commit}")
    tracked_changes = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if tracked_changes:
        raise RuntimeError("Tracked worktree changes exist; commit them before building the review bundle.")

    output_root = (ROOT / args.output_root).resolve()
    bundle = output_root / args.name
    archive = output_root / f"{args.name}.zip"
    sidecar = output_root / f"{args.name}.zip.sha256"
    for target in (bundle, archive, sidecar):
        if target.exists():
            raise RuntimeError(f"Refusing to overwrite existing output: {target}")

    (bundle / "assets").mkdir(parents=True)
    (bundle / "rendered-wiki").mkdir()
    (bundle / "rendered-docs").mkdir()
    (bundle / "maintained-html").mkdir()
    (bundle / "assets" / "review.css").write_text(REVIEW_CSS, encoding="utf-8")

    for filename, title in WIKI_SOURCES.items():
        source = ROOT / "wiki" / filename
        text = rewrite_markdown_links(
            source.read_text(encoding="utf-8"), source, "wiki", args.source_commit
        )
        output = bundle / "rendered-wiki" / f"{source.stem}.html"
        output.write_text(
            document_wrapper(title, repository_path(source), args.source_commit, render_markdown(text)),
            encoding="utf-8",
        )

    for relative, (output_name, title) in DOC_SOURCES.items():
        source = ROOT / relative
        text = rewrite_markdown_links(
            source.read_text(encoding="utf-8"), source, "docs", args.source_commit
        )
        output = bundle / "rendered-docs" / output_name
        output.write_text(
            document_wrapper(title, relative, args.source_commit, render_markdown(text)),
            encoding="utf-8",
        )

    maintained = bundle / "maintained-html"
    shutil.copy2(ROOT / "docs" / "towerscout-docs.css", maintained / "towerscout-docs.css")
    for filename in MAINTAINED_HTML:
        source = ROOT / "docs" / filename
        transformed = rewrite_maintained_links(
            source.read_text(encoding="utf-8"), source, args.source_commit
        )
        (maintained / filename).write_text(transformed, encoding="utf-8")
    (maintained / "app-route-note.html").write_text(route_note(), encoding="utf-8")

    instructions = (ROOT / args.instructions).resolve()
    instructions_text = instructions.read_text(encoding="utf-8")
    (bundle / "REVIEWER-INSTRUCTIONS.md").write_text(instructions_text, encoding="utf-8")
    (bundle / "reviewer-instructions.html").write_text(
        document_wrapper(
            "Round 5 Reviewer Instructions",
            repository_path(instructions),
            args.source_commit,
            render_markdown(instructions_text),
            prefix="",
        ),
        encoding="utf-8",
    )
    (bundle / "index.html").write_text(
        index_html(args.source_commit, args.branch), encoding="utf-8"
    )
    (bundle / "SOURCE.txt").write_text(
        source_record(args.source_commit, args.branch), encoding="utf-8"
    )

    checksum_paths = sorted(
        path for path in bundle.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    checksum_text = "".join(
        f"{sha256(path)}  {path.relative_to(bundle).as_posix()}\n" for path in checksum_paths
    )
    (bundle / "SHA256SUMS.txt").write_text(checksum_text, encoding="utf-8")

    html_count, checked_links = validate_links(bundle)

    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in sorted(path for path in bundle.rglob("*") if path.is_file()):
            member = PurePosixPath(args.name) / PurePosixPath(path.relative_to(bundle).as_posix())
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"Unsafe ZIP member: {member}")
            handle.write(path, member.as_posix())

    with zipfile.ZipFile(archive) as handle:
        members = handle.namelist()
        if len(members) != len([path for path in bundle.rglob("*") if path.is_file()]):
            raise RuntimeError("ZIP/file count mismatch")
        for member in members:
            relative = Path(*PurePosixPath(member).parts[1:])
            if hashlib.sha256(handle.read(member)).hexdigest() != sha256(bundle / relative):
                raise RuntimeError(f"ZIP content mismatch: {member}")

    archive_hash = sha256(archive)
    sidecar.write_text(f"{archive_hash}  {archive.name}\n", encoding="utf-8")
    print(f"bundle={bundle}")
    print(f"archive={archive}")
    print(f"sha256={archive_hash}")
    print(f"files={len([path for path in bundle.rglob('*') if path.is_file()])}")
    print(f"html_pages={html_count}")
    print(f"local_links_checked={checked_links}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
