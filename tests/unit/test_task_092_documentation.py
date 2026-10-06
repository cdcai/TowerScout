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
        "support has confirmed",
        "changes the assigned path",
        "first-cohort",
        "towerscoutuat",
        "owner-provided",
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
        "docs/local-it-administrator-guide.md",
        "docs/local-it-administrator-guide.html",
        "wiki/Home.md",
        "wiki/Before-You-Install.md",
        "wiki/Choose-Your-Setup.md",
        "wiki/Install-And-First-Run.md",
        "wiki/Google-And-Azure-API-Credentials.md",
        "wiki/Everyday-Commands.md",
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
        assert "open the working folder" in text[verify_at:extract_at], relative_path
        assert "click the address bar" in text[verify_at:extract_at], relative_path
        assert "type `powershell`" in text[verify_at:extract_at], relative_path


def test_maintained_html_keeps_core_user_actions_and_responsive_commands():
    quick_start = _read("docs/quick-start.html")
    user_guide = _read("docs/user-guide.html")
    stylesheet = _read("docs/towerscout-docs.css")

    assert 'href="towerscout-docs.css"' in quick_start
    assert "command-grid" in quick_start
    assert "<table" not in quick_start
    assert "minmax(min(100%, 30rem), 1fr)" in stylesheet
    for command in (
        r".\setup-towerscout.cmd -Engine docker -Gpu off",
        r".\setup-towerscout.cmd -Engine docker -Gpu on",
        r".\setup-towerscout.cmd -Engine podman -Gpu off",
        r".\setup-towerscout.cmd -Engine podman -Gpu on",
    ):
        assert command in quick_start
    for label in ("Circle", "Custom shape", "Clear all", "Stop When Finished Or Resume Later"):
        assert label in user_guide


def test_quick_start_markdown_and_html_keep_critical_setup_details_in_sync():
    for relative_path in ("docs/quick-start.md", "docs/quick-start.html"):
        text = _read(relative_path)
        for phrase in (
            "Maps JavaScript API",
            "Places API (New)",
            "Maps Static API",
            "Geocoding API",
            "Application restrictions: None",
            "selected_device=cuda",
            "enable-podman-gpu.ps1",
            "podman-gpu-user-guide.md",
        ):
            assert phrase in text, (relative_path, phrase)


def test_package_guide_covers_both_variants_and_separates_tls_phases():
    text = _read("docs/package-guide.md")
    verify_at = text.index("## Required Download Verification For The Unsigned Package")
    extract_at = text.index("## Application Package Layout")
    verification = text[verify_at:extract_at]
    assert "*-cpu.zip" in verification
    assert "*-cuda128.zip" in verification
    assert "certutil -hashfile .\\towerscout-<release-version>-cpu.zip" in verification
    assert "certutil -hashfile .\\towerscout-<release-version>-cuda128.zip" in verification

    diagnostic_at = text.index("### Diagnostic Only")
    review_at = text.index("### Review And Obtain Approval")
    apply_at = text.index("### Apply The Approved Change")
    assert diagnostic_at < review_at < apply_at


def test_wiki_tls_repair_is_discoverable_and_preserves_safe_phases():
    credentials = _read("wiki/Google-And-Azure-API-Credentials.md")
    install = _read("wiki/Install-And-First-Run.md")
    troubleshooting = _read("wiki/Troubleshooting-And-Safe-Support.md")

    repair_link = (
        "Troubleshooting-And-Safe-Support#local-it-certificate-work"
    )
    assert repair_link in credentials
    assert repair_link in install

    assert "CERTIFICATE_VERIFY_FAILED" in troubleshooting
    assert (
        r".\scripts\repair-provider-tls.cmd -Provider google -Engine docker "
        r"-Gpu off -Port 5000"
    ) in troubleshooting
    assert "run one diagnostic command\n   without `-Apply`" in troubleshooting
    assert "complete command printed\n   by the diagnostic" in troubleshooting
    assert r"docs\package-guide.md" in troubleshooting
    assert "Do not disable TLS verification" in troubleshooting


def test_setup_fallback_examples_preserve_the_users_selected_configuration():
    for relative_path in (
        "docs/quick-start.md",
        "docs/quick-start.html",
        "docs/package-guide.md",
        "docs/local-it-administrator-guide.md",
        "docs/local-it-administrator-guide.html",
    ):
        text = _read(relative_path)
        normalized = text.lower()
        assert "-PackageZip" in text, relative_path
        assert "-AssetZip" in text, relative_path
        assert "-engine" in normalized and "-gpu" in normalized, relative_path
        assert "preserve" in normalized or "keep" in normalized, relative_path


def test_wiki_orders_credentials_before_install_and_separates_daily_actions():
    choice = _read("wiki/Choose-Your-Setup.md")
    credentials = _read("wiki/Google-And-Azure-API-Credentials.md")
    everyday = _read("wiki/Everyday-Commands.md")

    assert "Next, follow [Google And Azure API Credentials]" in choice
    assert "Next, continue with [Install And First Run]" in credentials
    assert everyday.index("## Start Or Reopen TowerScout") < everyday.index("## Check Status")
    assert everyday.index("## Check Status") < everyday.index("## Stop When Finished")

    fenced_blocks = everyday.split("```")
    for block in fenced_blocks[1::2]:
        assert not ("start.bat" in block and "stop.cmd" in block)


def test_privacy_warning_precedes_user_export_actions():
    markdown = _read("docs/user-guide.md")
    html = _read("docs/user-guide.html")
    assert markdown.index("Confirm that the results and their locations") < markdown.index("Use `Download results`")
    assert html.index("<strong>Privacy:</strong>") < html.index("Download results")


def test_novice_terminal_circle_and_podman_restart_instructions_are_complete():
    for relative_path in (
        "docs/quick-start.md",
        "docs/quick-start.html",
        "wiki/Before-You-Install.md",
    ):
        text = _read(relative_path)
        assert "Windows PowerShell" in text, relative_path
        assert "Start" in text, relative_path
        assert "normal window" in text, relative_path
        assert "administrator" in text, relative_path

    user_guide = _read("docs/user-guide.md")
    circle = user_guide[user_guide.index("### Circle Search"):]
    assert circle.index("Select `Circle`") < circle.index("Click the map to place the circle")
    assert circle.index("Click the map to place the circle") < circle.index("Select `Estimate tiles`")

    everyday = _read("wiki/Everyday-Commands.md")
    shared_podman = everyday.index("Before either Podman command")
    podman_cpu = everyday.index("### Podman CPU")
    podman_gpu = everyday.index("### Podman NVIDIA GPU")
    assert shared_podman < podman_cpu < podman_gpu


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
