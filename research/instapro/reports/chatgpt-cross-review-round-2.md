# InstaPro — ChatGPT Cross-Review of Perplexity and Claude (Round 2)

- Reviewer: ChatGPT (GPT-6)
- Date: 2026-11-21
- Reports reviewed:
  - `reports/perplexity-computer-claude-opus-5.5.md` — transcription of the supplied two-page PDF summary
  - `reports/claude-sonnet-5.5-round-1.md` — supplied Claude review
  - `reports/chatgpt-gpt-6-technical-audit-round-1.md` — independent technical audit

## 1. Shared conclusions

1. **Separate fast chat from long-running jobs.** Both reviewers separate browser/provider streaming from asynchronous task execution. This is the correct performance boundary: Actions runner startup and queueing do not belong in the interactive token-stream path.
2. **Never expose provider credentials in public browser code or public repository files.** Both reports recognize that provider keys and GitHub credentials need a user-controlled secret boundary.
3. **Keep the MVP narrow.** Both defer broader provider coverage and browser automation until the first path works.
4. **Use explicit quotas and bounded execution.** Both recommend a Resource Governor, timeouts, and concurrency controls.

## 2. Material disagreement / correction

### GitHub Actions as the async execution backend

Claude recommends short, bounded Actions jobs and says to check the terms before launch. Perplexity raises a stronger concern: GitHub's terms restrict offering Actions or elements of Actions as part of a commercial application/service and restrict unrelated activity on GitHub-hosted runners.

**ChatGPT position:** Claude's mitigation is incomplete. Merely making jobs short or moving them to self-hosted runners does not automatically resolve the commercial-offering restriction. The official terms say the relevant restrictions apply regardless of whether an Action uses self-hosted runners. Therefore:
- Do not treat GitHub Actions as an approved general-purpose InstaPro agent runtime.
- Retain Actions for the user's associated software-project build, test, deployment, or publication workflows.
- Obtain written clarification from GitHub before relying on Actions as an execution feature of a commercial agent product.
- For general agent tasks, prove a user-controlled local/device process or independently user-operated compute path.

This is a product feasibility gate, not a reason to abandon GitHub for identity, repository storage, configuration, audit trail, and software CI/CD.

## 3. Authentication comparison

Claude recommends a GitHub App plus a tiny token-exchange Worker and states that a pure-static app cannot safely perform the OAuth code exchange. Perplexity says a static page cannot complete GitHub sign-in without a small backend/function, or else a PAT must be pasted manually.

**Correction / nuance:** a static client can initiate GitHub authorization and GitHub documents public-client authorization with PKCE. However, a browser bundle cannot keep a client secret confidential, and token storage in a public client is a meaningful security concern. A small backend/token broker is the safer web-app design; a PAT is a prototype-only fallback, not a production sign-in architecture.

**Decision:** prefer a GitHub App with minimal permissions and a small token-exchange component if a free and acceptable deployment option is available. If zero-server is absolute, explicitly downgrade the prototype's authentication/security guarantees rather than claiming production-grade GitHub sign-in.

## 4. Resource Governor assessment

Both reviewers propose limits checked at workflow start. Claude adds max runs/day, max steps, max tokens/task, concurrency, and cancellation; Perplexity proposes a `governor.yml` check plus timeout and concurrency.

These are useful controls but not a complete hard budget:
- A first-step check happens after a runner has already started.
- A local counter in repository files may race under concurrent runs unless updates are serialized.
- Token limits need provider-side accounting or reliable usage responses; a configured maximum alone does not prove actual spend.
- Cancellation is useful but cannot guarantee zero cost for work already performed.

**MVP decision:** for any permitted Actions workflow, use a hard job timeout, concurrency group, maximum steps/retries, and a preflight quota check. Track observed usage after each run. Do not describe this as a guaranteed financial ceiling.

## 5. Open-source components and evidence quality

Claude correctly lists no repositories or licenses as verified rather than inventing a shortlist. Perplexity mentions Vercel AI SDK and rejects Open WebUI on licensing grounds, but the supplied two-page summary does not include a precise version/license analysis or sufficient maintenance evidence.

**Decision:** neither component choice is approved solely on these summaries. Verify exact repository, license file, version, maintenance signal, and browser/provider compatibility before adoption. The smallest MVP can first test a direct official provider API without committing to a broad framework.

## 6. Revised decision log

| Area | Decision |
|---|---|
| Fast chat | Browser-to-official-provider streaming with the user's own key, only where browser access/CORS and provider terms support it; otherwise a user-controlled proxy/local process |
| GitHub identity | GitHub App with minimal permissions; token broker preferred for a web app |
| General async agent runtime | Not approved on GitHub Actions pending written policy clarification |
| GitHub Actions | Keep for associated software-project CI/CD and other clearly permitted repository workflows |
| Memory | Private user repository files for a minimal prototype; avoid storing secrets or sensitive content |
| Resource Governor | Bounded execution controls and observed usage; do not promise a hard cost ceiling |
| Open-source dependencies | No adoption until exact license and maintenance evidence are recorded |
| Browser automation | Defer |

## 7. What changed after cross-review?

The overall verdict remains **Revise**. The two reports reinforce the fast/async split and user-owned credentials, but Claude's suggestion to rely on short bounded Actions jobs does not resolve the policy concern identified in Perplexity's report and the independent audit. The key architecture decision is now clearer: GitHub remains the collaboration/control plane, but general agent compute must not depend on Actions unless the commercial-use boundary is clarified.

## Build now / Defer / First executable task

- **Build now:** a minimal mobile web chat proof using one official provider API and a user-supplied key, with a local-only or user-operated execution path for one bounded background task.
- **Defer:** general-purpose Actions orchestration, browser automation, multi-provider routing, and enterprise features.
- **First executable task:** prove one provider's streaming flow in the target browser, including CORS, cancellation, error handling, and ensuring the key is not written to public source, logs, or repository history. Record a reproducible pass/fail result.
