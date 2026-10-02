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
    assert "versioned `docs` folder" in home
    assert "authoritative release record" in install
    assert "final release is not yet frozen or published" in releases.lower()


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


def test_current_user_docs_do_not_require_project_assigned_pathways():
    prohibited = (
        "support-assigned",
        "support assigned",
        "support-selected",
        "support selected",
        "support explicitly assigns",
        "changes the assigned path",
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
        "wiki/Home.md",
        "wiki/Before-You-Install.md",
        "wiki/Choose-Your-Setup.md",
        "wiki/Install-And-First-Run.md",
    )

    for relative_path in current_docs:
        text = _read(relative_path).lower()
        for phrase in prohibited:
            assert phrase not in text, (relative_path, phrase)


def test_quick_start_explains_independent_choices_and_provider_acquisition():
    for relative_path in ("docs/quick-start.md", "docs/quick-start.html"):
        text = " ".join(_read(relative_path).lower().split())
        assert "three independent choices" in text, relative_path
        assert "google cloud console" in text, relative_path
        assert "azure portal" in text, relative_path
        assert "one credential per provider" in text, relative_path
        assert "browser can see" in text, relative_path


def test_engine_guides_verify_both_zips_before_extraction():
    for relative_path in (
        "docs/docker-cpu-user-guide.md",
        "docs/docker-gpu-user-guide.md",
        "docs/podman-cpu-user-guide.md",
        "docs/podman-gpu-user-guide.md",
    ):
        text = _read(relative_path).lower()
        verify_at = text.index("before extracting anything")
        extract_at = text.index("extract only the verified")
        assert verify_at < extract_at, relative_path
        assert "authoritative" in text[verify_at:extract_at], relative_path
        assert "get-filehash" in text[verify_at:extract_at], relative_path


def test_maintained_html_keeps_core_user_actions_and_responsive_commands():
    quick_start = _read("docs/quick-start.html")
    user_guide = _read("docs/user-guide.html")

    assert 'href="towerscout-docs.css"' in quick_start
    assert "command-grid" in quick_start
    assert "<table" not in quick_start
    for label in ("Circle", "Custom shape", "Clear all", "Stop And Resume Later"):
        assert label in user_guide


def test_final_user_recovery_does_not_recommend_insecure_tls():
    for relative_path in (
        "docs/quick-start.md",
        "docs/quick-start.html",
        "docs/package-guide.md",
        "wiki/Troubleshooting-And-Safe-Support.md",
        "docs/support/oci-quick-start.md",
    ):
        text = _read(relative_path)
        assert "last-resort validation-only workaround" not in text, relative_path
        assert "```powershell\nTOWERSCOUT_ALLOW_INSECURE_TLS=1" not in text, relative_path
