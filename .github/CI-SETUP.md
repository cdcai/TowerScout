# CI bootstrap provenance

The receiving repository initially used a temporary validation bootstrap before
application adoption. That historical setup is superseded by the checked-in
workflows. `.github/workflows/ci.yml` defines current PR/main and weekly checks;
container publication and exact-digest verification remain manually dispatched
under explicit authorization. See `docs/maintenance.md` for approval and policy
boundaries. Fork rehearsal checks cannot replace destination merge checks.
