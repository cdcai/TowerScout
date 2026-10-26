# Deferred host helper

The Windows host-helper listener, worker, entrypoints and their PowerShell test
suite are removed from this adoption candidate. Active CI no longer executes
the helper suite or its self-test. The earlier development checkpoints preserve
that work; the deferred launcher redesign is not resumed by this adoption.

Endpoint protection blocked execution of the old helper script on a tested
host. Removal eliminates that script from the proposed source and package,
without changing endpoint protection or claiming compatibility with every
organization's security policy.

The Windows CI job retains its historical **Windows host-helper contracts**
check name to avoid silently changing the receiving repository's required-check
identity. It now runs supported package, provider and runtime contracts only.
A future check-name change requires the receiving owner's settings review.

The small state-cleanup library remains for launch and stop to invalidate stale
helper session files and environment values. An inherited
`TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED=1` setting warns and continues through
normal startup or shutdown because the helper implementation is absent.
The Python/frontend capability gates remain disabled. Neither stale metadata
nor that environment setting enables a browser-triggered repair operation.

Use the supported manual TLS repair and normal restart workflow:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

Select the engine and GPU mode for the intended installation. See the
[Package Guide](../package-guide.md) and [Quick Start](../quick-start.md).
Reintroducing a host listener would require a separate reviewed implementation
and security/endpoint qualification; it is outside this release scope.
