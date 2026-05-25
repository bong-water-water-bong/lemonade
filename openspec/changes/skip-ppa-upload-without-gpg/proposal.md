# Change Proposal: skip-ppa-upload-without-gpg

## Why

Fork CI should not fail only because Launchpad signing secrets are absent.
The reusable PPA upload workflow previously tried to import an empty
`GPG_PRIVATE_KEY`, causing forked repository CI to fail before upload steps.

At the same time, canonical release/upload workflows must not silently skip PPA
publishing when a signing key is expected.

## What Changes

- Add an `allow_skip_without_gpg` input to the reusable PPA upload workflow.
- Pass `allow_skip_without_gpg: ${{ github.event.repository.fork }}` from the
  Launchpad PPA workflow.
- Skip PPA upload cleanly only for forks without `GPG_PRIVATE_KEY`.
- Fail loudly for non-fork uploads when `GPG_PRIVATE_KEY` is missing.
- Validate that a configured GPG key imports at least one secret key before
  signing.

## Boundaries

- Owns: `.github/workflows/upload.yml`,
  `.github/workflows/launchpad-ppa.yml`.
- Consumes: `secrets.GPG_PRIVATE_KEY`,
  `github.event.repository.fork`.
- Emits: GitHub Actions notice for fork skips, GitHub Actions error for missing
  non-fork signing key.
- Must not touch: packaging scripts, Debian build actions, source package
  generation, PPA targets.

## Risks

- Boolean workflow-call inputs must remain compatible with GitHub Actions
  expression handling.
- Forks skip upload jobs by design; canonical repositories still need
  `GPG_PRIVATE_KEY` configured for upload jobs to pass.

## Verification

- [x] Repo-native YAML parse run for `.github/workflows/upload.yml` and
  `.github/workflows/launchpad-ppa.yml`.
- [x] Docs/wiki updated if durable knowledge changed.
- [x] OpenSpec tasks updated.
