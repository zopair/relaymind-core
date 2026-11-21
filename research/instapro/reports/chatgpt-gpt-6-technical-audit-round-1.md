# InstaPro — Independent Technical Audit of Perplexity Round 1

- Reviewer: ChatGPT (GPT-6)
- Review date: 2026-11-21
- Source reviewed: `reports/perplexity-computer-claude-opus-5.5.md` (transcription of the supplied two-page PDF summary)
- Verdict: **Revise — with one critical architecture/policy blocker**
- Scope: verify the three principal claims in the supplied summary against current official GitHub documentation. This is a technical product assessment, not legal advice.

## Executive decision

Do **not** make GitHub Actions the general-purpose execution backend for a commercial InstaPro agent. GitHub's current Additional Products and Features terms contain an explicit restriction on offering Actions or elements of Actions as part of a standalone or integrated commercial application/service. They also restrict GitHub-hosted runner activity unrelated to the software project associated with the repository. The restriction is stated to apply regardless of whether an Action uses self-hosted runners.

This does not prove that every customer-owned workflow triggered by a third-party product is prohibited. That boundary needs written clarification from GitHub/legal counsel. But it is a release-blocking risk for the proposed SaaS model if Actions is being offered as its execution engine.

**Practical MVP adjustment:** keep GitHub as identity, repository, audit trail, configuration, and software-project CI/CD integration. Do not market or depend on GitHub Actions as InstaPro's general agent compute service. Run general-purpose tasks in a user-controlled local process/device or in compute the user independently owns and operates, outside the product's provision of Actions as a service. Keep Actions use narrowly tied to building, testing, deploying, or publishing the user's associated software project unless GitHub confirms a broader permitted use.

## Claim-by-claim review

### 1. GitHub Actions terms — substantially confirmed; severity is higher than the summary suggests

The current GitHub terms page states:
- Actions must not be used to provide a standalone or integrated application/service offering Actions or elements of Actions for commercial purposes.
- GitHub-hosted runners must not be used for activity unrelated to production, testing, deployment, or publication of the software project associated with the repository.
- The listed restrictions apply regardless of whether an Action uses self-hosted runners.
- Misuse may lead to terminated jobs, restrictions, repository disabling, or account suspension/termination.

Source: https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features

**Correction to the supplied summary:** it is not enough to move non-code workloads from GitHub-hosted runners to self-hosted runners. The commercial-offering restriction is expressly written to apply regardless of runner type. A user-owned runner does not automatically remove that issue if InstaPro is still offering Actions as part of its commercial service.

**Decision:** treat Actions-as-general-agent-runtime as blocked pending written clarification. Do not rely on a broad interpretation that customer-owned repositories or self-hosted runners automatically make the model compliant.

### 2. GitHub Free limits — the cited figures are confirmed in current docs

The current Actions limits page lists GitHub Free with:
- 2,000 included minutes per month.
- 500 MB artifact storage.
- 10 GB cache storage per repository.

The billing documentation also shows these included amounts. Artifact storage is not the same as cache storage; they are separate quotas. The 500 MB artifact amount is shared with GitHub Packages storage according to GitHub's billing documentation.

Sources:
- https://docs.github.com/en/actions/reference/limits
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

**Correction:** the summary's “500 MB artifacts” figure is accurate, but the architecture must not conflate it with the separate 10 GB cache allowance. Minutes and storage allowances can change and must be rechecked before release.

**Decision:** implement a governor for quotas and usage visibility, but never describe the platform as unlimited or cost-free at scale.

### 3. GitHub sign-in from a static frontend — the summary's categorical conclusion is too strong

GitHub documents a GitHub App web application flow for browser apps. It supports redirecting to GitHub, receiving a callback code, using `state`, and PKCE (S256). The subsequent token exchange requires the GitHub App client secret.

GitHub's own best-practices documentation explicitly says a single-page/public client cannot keep the client secret confidential and will have to ship it in application code if it uses that public-client approach; PKCE is recommended. It also warns that public clients are trivially spoofable and recommends that websites/web apps encrypt tokens on their backend.

Sources:
- https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app
- https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app

**Correction:** a static page can initiate the GitHub authorization flow, and GitHub documents a public-client/PKCE approach. However, that does not make it a sound trust boundary for a commercial service or for protecting service-side resources. The client secret is not secret in a public bundle, and browser storage of access/refresh tokens carries risk.

**Decision:** for the MVP, use GitHub App authorization with a minimal-permission design and a small token-exchange component only if a genuinely free, acceptable backend is available. If the zero-server requirement is absolute, evaluate a user-driven device/desktop authorization flow or a user-supplied fine-grained PAT as a clearly labelled prototype-only path; do not represent that as production-grade centralized sign-in. Device flow has phishing considerations noted by GitHub and should not be enabled casually.

## Review of the proposed components

### Vercel AI SDK
The summary proposes direct browser-to-provider streaming using the user's provider key. This can avoid company-funded inference, but the SDK does not remove provider-specific credential and CORS constraints. A provider must explicitly support browser-origin requests, or a user-controlled proxy/local process is needed. Do not assume all listed providers expose safe browser-compatible endpoints.

**MVP decision:** first prove one provider end-to-end from the target browser with the user's own key, including CORS, streaming, error handling, and key lifetime. Add other providers only after the adapter passes the same test.

### workflow_dispatch and Resource Governor
The GitHub REST API supports dispatching workflows, but API capability does not override Actions product terms. A `governor.yml` check at the start of a workflow can stop subsequent work; it cannot undo runner startup or guarantee a hard financial ceiling on its own. `timeout`, `concurrency`, and an explicit per-run budget are useful safeguards, not permission to use Actions for any workload.

**MVP decision:** retain dispatch only for permitted software-project tasks. Enforce a run budget before expensive steps, set a strict timeout and concurrency group, and make every task idempotent with a maximum retry count.

### Open WebUI
The supplied summary says Open WebUI was rejected because its license has additional conditions, but this PDF does not identify the exact version, license text, relevant clause, or comparison with the intended distribution model.

**Decision:** unresolved. Do not treat the rejection as verified until the exact repository version and license are cited and checked against the intended use. Also do not adopt it until that check is complete.

## Smallest practical next step

1. Keep the current shared research branch; do not merge to `main`.
2. Mark GitHub Actions as **not approved for general agent execution** until GitHub clarifies the commercial-use boundary in writing.
3. Build a narrow technical spike: GitHub App login/authorization + one provider's browser streaming + user-owned task execution outside Actions.
4. Keep Actions only for a test workflow that builds/tests/deploys the InstaPro software repository itself.
5. Record pass/fail evidence: OAuth/token flow, provider streaming, secret exposure scan, task completion, cancellation, and quota guard behavior.

## Claims not established by the supplied PDF

- It does not provide the full A–H technical report, Mermaid architecture, verified repository shortlist, exact Open WebUI license analysis, or test logs.
- It does not prove that a general agent workload is permitted on GitHub Actions.
- It does not prove that a static-only GitHub App login is impossible.
- It does not prove the proposed Resource Governor is implemented or effective.
- It does not establish provider browser CORS support for Claude, Gemini, Grok, or Perplexity.

## Final position

**Revise.** Keep the GitHub-native collaboration and project-management parts. Remove the assumption that GitHub Actions can serve as InstaPro's general-purpose commercial agent runtime. Prove the smallest alternative before expanding the architecture.

---
*This report distinguishes statements found in the supplied PDF from conclusions verified against the official documentation linked above. It is a technical review, not legal advice.*
