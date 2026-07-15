# Zume 1.0 Release Runbook

## Release model

One product release, multiple controlled phase commits.

Branch:
`release/zume-1.0`

Final intended tag after human UI review:
`v1.0.0`

## Builder sequence

1. Verify baseline.
2. Create release branch.
3. Complete each phase and gate.
4. Commit each phase.
5. Run local full validation.
6. Build release zip.
7. Push release branch.
8. Open/update draft PR.
9. Run/watch central CI.
10. Produce builder reports.
11. Stop.

Builder does not merge or tag.

## Validator sequence

1. New Cursor chat/agent.
2. Clean worktree/clone.
3. Run clean-room validator prompt.
4. Publish clean-room report.
5. Stop.

Validator does not merge or tag.

## Human/Cowork review

Review:

- Home;
- Question Library;
- Practice Session;
- Interview Builder;
- Candidate Intake/Finalize;
- Exercise Lab;
- Ask Zume;
- audio controls;
- desktop/tablet screenshots;
- representative candidate documents.

Record only defects, not redesign requests, unless a critical usability problem
is proven.

## Merge and tag criteria

Required:

- clean-room verdict `READY FOR HUMAN UI REVIEW`;
- human screen review accepted;
- central CI green;
- no high/critical security finding;
- no candidate PII/secrets;
- release zip checksum;
- known limitations documented.

Then:

1. merge PR using the repository’s normal strategy;
2. rerun CI on `main`;
3. create annotated `v1.0.0` tag;
4. attach release zip/checksum if desired;
5. protect `main` from force pushes/deletion and require CI.

## Post-release rule

Freeze feature expansion for the first operational cycle.

Run real workflows locally:

- intake;
- interview;
- finalize;
- export;
- archive;
- preparation session;
- Ask Zume;
- read aloud;
- one exercise in each supported runner.

Only defect-driven changes go into `v1.0.1`.
