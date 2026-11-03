# Release checklist

The current repository is a starter preview. Publishing a repository is not a stable release.

- [ ] Resolve the V0.1 release-blocking roadmap items or document accepted exceptions.
- [ ] Run `make check`, MinIO integration, real-model and Docling acceptance tests.
- [ ] Build and smoke-test the exact container on Linux amd64 and arm64.
- [ ] Verify backup/restore, restart recovery and known-query behavior.
- [ ] Review dependency/model licenses, vulnerabilities and pinned base-image digests.
- [ ] Set up a private conduct-reporting channel and verify vulnerability reporting.
- [ ] Update changelog, version in Python/frontend, compatibility and upgrade notes.
- [ ] Generate SBOM, provenance and checksums; sign artifacts and record verification steps.
- [ ] Create a reviewed tag and GitHub release with explicit tested limits.
- [ ] Publish the container only after its exact digest passes acceptance.
- [ ] Rehearse the README from a clean machine; replace launch/logo placeholders.
- [ ] Enable branch protection requiring CI after checking available account settings.

There is intentionally no automatic package/container publishing workflow yet.
