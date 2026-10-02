from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

WIKI_PAGES = (
    "Home.md",
    "Before-You-Install.md",
    "Choose-Your-Setup.md",
    "Install-And-First-Run.md",
    "Google-And-Azure-API-Credentials.md",
    "Everyday-Commands.md",
    "Docker-Guidance.md",
    "Podman-Guidance.md",
    "NVIDIA-GPU-Setup.md",
    "Troubleshooting-And-Safe-Support.md",
    "Local-IT-Administrator-Guide.md",
    "Demo-Video-And-Written-Walkthrough.md",
    "Releases-And-Supported-Versions.md",
    "Licensing-Privacy-And-Provider-Terms.md",
)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_required_wiki_draft_pages_and_sidebar_are_complete():
    sidebar = _read("wiki/_Sidebar.md")

    for filename in WIKI_PAGES:
        path = ROOT / "wiki" / filename
        assert path.is_file(), filename
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "Last reviewed" in normalized, filename
        assert "Publication state" in text, filename
        assert path.stem in sidebar or filename == "Home.md", filename


def test_wiki_keeps_release_and_package_authority_explicit():
    home = _read("wiki/Home.md")
    install = _read("wiki/Install-And-First-Run.md")
    releases = _read("wiki/Releases-And-Supported-Versions.md")

    assert "release record" in home
    assert "docs\\" in home
    assert "authoritative release record" in install
    assert "not yet publicly frozen/published" in releases.lower()


def test_local_it_guide_is_packaged_and_exposed_in_app():
    package_script = _read("scripts/package-release.ps1")
    public_docs = _read("webapp/towerscout.py")
    template = _read("webapp/templates/towerscout.html")

    for filename in (
        "local-it-administrator-guide.md",
        "local-it-administrator-guide.html",
    ):
        assert (ROOT / "docs" / filename).is_file()
        assert filename in package_script
        assert filename in public_docs

    assert "/docs/local-it-administrator-guide.html" in template


def test_quick_start_documents_observed_explicit_zip_path_fallback():
    for relative_path in ("docs/quick-start.md", "docs/quick-start.html"):
        text = _read(relative_path)
        assert "-PackageZip" in text, relative_path
        assert "-AssetZip" in text, relative_path
        assert "authoritative release record" in text, relative_path


def test_current_primary_docs_do_not_claim_stale_release_scope():
    stale_phrases = (
        "through the RC7",
        "through the stable `v0.1.0` closeout",
        "through the stable v0.1.0 closeout",
        "For the July 2026 pilot",
        "RC5",
        "primary pilot",
        "default pilot Azure",
    )
    current_docs = (
        "README.md",
        "docs/quick-start.md",
        "docs/quick-start.html",
        "docs/package-guide.md",
        "docs/project-overview.md",
        "docs/project-overview.html",
        "docs/user-guide.md",
        "docs/user-guide.html",
        "docs/docker-cpu-user-guide.md",
        "docs/docker-gpu-user-guide.md",
        "docs/podman-cpu-user-guide.md",
        "docs/podman-gpu-user-guide.md",
        "docs/support/oci-quick-start.md",
        "docs/support/oci-runtime-contract.md",
    )

    for relative_path in current_docs:
        text = _read(relative_path)
        for stale_phrase in stale_phrases:
            assert stale_phrase not in text, (relative_path, stale_phrase)
