# Zume web workspace

React/Vite workspace for the local Zume API. It proxies `/api` to
`http://127.0.0.1:8787` during development and writes production assets to
`apps/web/dist`, which the Python server discovers automatically.

## Run

```powershell
cd apps/web
npm install
npm run dev
```

The local API is expected to be running separately on port 8787.

## API assumptions

The UI targets the documented `/api` endpoints. Search responses may expose
either `items` or `questions`; question records should provide `id` and may
provide `question` (or `prompt`), `domain`, `level`, and `priority`. Submission
responses are rendered as local operational records without treating a resume
evidence coverage percentage as a competency score.

Candidate intake currently accepts pasted resume text because the agreed API
contract contains `resume_text`, not multipart file upload. File intake remains
available through the local `zume intake` CLI until the API supports uploads.
