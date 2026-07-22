# Launchpad PPA CI

The `Launchpad PPA` workflow builds Debian source packages for pushes and
binary packages for pull requests.

PPA upload is handled by the reusable `.github/workflows/upload.yml` workflow.
That workflow needs `secrets.GPG_PRIVATE_KEY` to sign source package changes
before `dput` uploads them to Launchpad.

Forks are allowed to run CI without Launchpad signing secrets. In forked
repositories, `launchpad-ppa.yml` passes
`allow_skip_without_gpg: ${{ github.event.repository.fork }}` to the reusable
upload workflow. When this flag is true and `GPG_PRIVATE_KEY` is absent, upload
steps are skipped with a GitHub Actions notice.

Canonical repositories must fail loudly when `GPG_PRIVATE_KEY` is missing. This
prevents release or bleeding-edge uploads from appearing green while publishing
nothing.
