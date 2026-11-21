# Perplexity Computer — InstaPro Round 1 Review

> Source: user-uploaded two-page PDF, received 2026-11-21.
> Scope note: this Markdown file is a faithful text transcription of the supplied PDF summary. It is **not** the full underlying technical report or the original PDF binary.

## Review result

**Verdict: Revise.**

The review was written in the requested A–H format. This is the first report in Round 1. No reports from other models were available in the branch, so the cross-review section remains empty.

## Three main findings

### 1. GitHub Actions policy and workload restrictions

The report claims GitHub Actions terms restrict use as a commercial service and limit the types of tasks that may run on GitHub-hosted runners. It argues that activities unrelated to the software project in the repository—such as research, shopping, or social-media publishing—could expose a general-purpose agent MVP to account suspension.

Suggested response in the report:
- Limit the MVP to code-related work in the user's repository.
- Defer other tasks to a runner on the user's own device.
- Obtain legal advice on the “commercial service” clause before launch.

**Verification status:** Claim reproduced from the supplied report; not independently verified in this document.

### 2. GitHub Actions free-plan limits and repository privacy

The report states:
- The free plan includes approximately 2,000 Linux minutes per month.
- Private repositories have a 500 MB artifact allowance.
- The repository should be private because the agent's memory is stored in the repository and a public repository could expose user data.

**Verification status:** Figures and interpretation reproduced from the supplied report; current plan-specific limits and applicable storage rules require independent verification.

### 3. GitHub sign-in from a static page

The report says GitHub sign-in cannot be completed securely from a static GitHub Pages endpoint alone because exchanging the code requires a small backend/function, and recommends a manually pasted PAT for the experimental version.

**Verification status:** The security concern about exposing a client secret in browser code is valid as a design constraint, but the report's categorical statement that static sign-in is impossible needs qualification. GitHub OAuth App and GitHub App flows have different requirements; a GitHub App user authorization flow and a backend-mediated code exchange should be evaluated before settling on a PAT-only MVP.

## Proposed architecture in the report

- **Fast chat:** Browser-to-provider streaming using the user's own key, with Vercel AI SDK (Apache-2.0).
- **Long-running tasks:** Trigger a workflow in the user's repository using `workflow_dispatch`, with the run consuming the user's API key.
- **Resource Governor:** Stop usage when the budget is reached, without an additional service. Read `governor.yml` at the first step of each run and apply `concurrency` and `timeout`.
- **Component selection:** The report says it reviewed GitHub API and component licenses/maintenance, and rejected Open WebUI as a base because its license has additional conditions.

**Verification status:** These are the reviewer's proposals and claims, not confirmed implementation results.

## Next step stated by the reviewer

The reviewer said the report had not been uploaded to the branch because upload required explicit permission, and asked whether it should be committed to:

`research/instapro/reports/perplexity-computer-claude-opus-5.5.md`

The supplied PDF is titled **InstaPro Round 1 Review — Perplexity Computer**.

## References listed in the supplied PDF

1. https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features
2. https://docs.github.com/en/actions/reference/limits
3. https://docs.github.com/en/rest/actions/workflows
4. https://ai.google.dev/gemini-api/docs/openai
5. https://docs.ollama.com/api/openai-compatibility
6. https://docs.x.ai/docs/api-reference
7. https://github.com/anthropics/anthropic-sdk-typescript
8. https://docs.github.com/en/billing/concepts/budgets-and-alerts
9. https://docs.github.com/en/billing/concepts/product-billing/github-actions
10. https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
11. https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/refreshing-user-access-tokens
12. https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
13. https://docs.anthropic.com/en/api/client-sdks
14. https://docs.perplexity.ai/guides/chat-completions-guide

## Cross-review

Pending: no other model reports were present in the shared review folder when this file was prepared.
