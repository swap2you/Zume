# Exercise Lab

The Exercise Lab runs preparation exercises through configured local runners.
It is not a candidate answer-sharing system.

## Runners

- SQL uses local SQLite fixtures.
- API exercises target the bundled local mock API in `training/mock-api`.
- Java and Selenium are Docker-isolated when Docker is installed and
  `ZUME_ENABLE_DOCKER_LABS` is explicitly enabled.

Run `zume doctor` to see available capabilities. Docker is optional and no
Docker image is included in the Windows release package. Lab workspaces and
temporary outputs live under git-ignored `data/lab-workspaces/`.

Never put candidate submissions, reference solutions, or interviewer-only
answers into shareable materials. Only `04_Candidate_Exercise_Sheet.docx` may
be shared with a candidate.
