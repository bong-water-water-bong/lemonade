# Tasks: skip-ppa-upload-without-gpg

## Setup

- [x] Confirm scope and owner.
- [x] Confirm verification commands.

## Implementation

- [x] Add missing-key detection to the reusable PPA upload workflow.
- [x] Allow missing GPG key skips only when the caller repository is a fork.
- [x] Keep non-fork PPA upload failures loud when the signing key is absent.
- [x] Validate imported GPG key material before signing.

## Verification

- [x] Run repo-native tests/checks.
- [x] Update docs/wiki if durable knowledge changed.
- [x] Ready for review.
