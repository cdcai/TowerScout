# Releases And Supported Versions

> **Audience:** All users. **Applies to:** Public TowerScout releases.
> **Last reviewed:** 2026-10-02. **Publication state:** Local draft; the next
> final release is not yet frozen or published.

Use the [TowerScout Releases page](https://github.com/J-Schulein/TowerScout/releases)
as the public download source. Choose only the entry whose notes identify it
as the current supported final Windows release.

For that entry, confirm:

- it is not labeled **Draft** or **Pre-release** for ordinary end-user use;
- its notes name the exact supported Windows, engine, CPU/GPU, provider, and
  known-limitation scope;
- it lists one CPU and one CUDA Application Package plus the shared Model &
  Data Package and matching checksum files;
- it displays authoritative SHA-256 values for both ZIPs; and
- the Application Package manifest names a digest-pinned container image.

GitHub's automatic source archives are for source review, not package
installation. A mutable image tag, sidecar downloaded beside a ZIP, or newer
version number alone does not establish the supported release identity.

The published `v0.1.2` pilot remains historical and immutable. The local
`rc4` artifacts were a preliminary diagnostic baseline, not the final
documentation-aligned release. The next final release will have new package
hashes and image digests after documentation is frozen and rebuilt.
