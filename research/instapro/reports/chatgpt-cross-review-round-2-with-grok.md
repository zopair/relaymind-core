# InstaPro — ChatGPT Cross-Review Including Grok (Round 2)

- Reviewer: ChatGPT (GPT-6)
- Date: 2026-11-21
- Reports reviewed:
  - `reports/perplexity-computer-claude-opus-5.5.md` — supplied two-page PDF transcription
  - `reports/claude-sonnet-5.5-round-1.md`
  - `reports/grok-round-1.md`
  - `reports/chatgpt-gpt-6-technical-audit-round-1.md`
  - `reports/chatgpt-cross-review-round-2.md`

## 1. Consensus strengthened by Grok

All three external reviewers and the independent audit converge on these points:

1. Fast chat must not run through GitHub Actions; streaming belongs in the browser-to-provider path (subject to provider CORS/API rules) or a minimal user-approved proxy.
2. User-owned provider credentials must never be embedded in public browser code or public repository files.
3. A GitHub App with narrowly scoped permissions is preferable to a broad OAuth scope or long-lived PAT for a web product.
4. Resource controls should be simple, bounded, and testable.
5. Browser automation, broad multi-provider routing, and enterprise features should be deferred until the narrow MVP works.

Grok adds a clear severity assessment: GitHub Actions terms risk is **Critical** until GitHub clarifies the commercial-service boundary in writing. This aligns with the independent audit's release-blocking treatment.

## 2. Important internal inconsistency in Grok's proposal

Grok's executive recommendation says general agent work should run in the browser or on user-controlled compute outside Actions, and its risk table says to move general agent work off Actions. However, the architecture diagram, core decisions, Phase 0/1 roadmap, and first executable task still route long/async tasks through `workflow_dispatch` and GitHub Actions.

This is not fully reconciled. It matters because the first executable task Grok proposes—dispatching a prompt, calling Claude/Grok, and writing a result file—looks like a general-purpose agent task unless it is strictly tied to building, testing, deploying, or publishing the user's associated software project.

**Decision:** do not implement that workflow as the InstaPro general agent MVP until GitHub confirms the relevant use is permitted. If retained as a technical spike, scope it narrowly to a software-project workflow and record that scope in the test repository.

## 3. GitHub App and Worker

Claude and Grok both recommend a GitHub App plus a small token-exchange Worker. This is the most consistent web-app direction in the reports, but it adds a runtime component and operational dependency, so it is not literally zero-server.

**Decision:** treat a tiny token broker as the preferred web-auth option only if a free tier is sufficient, the provider's terms permit the use, and token handling is implemented without exposing app secrets. If the zero-server constraint is absolute, explicitly label the static/PAT prototype as reduced-assurance rather than calling it production-grade sign-in.

## 4. Open-source components: not yet accepted

Grok lists Vercel AI SDK (Apache-2.0), Anthropic TypeScript SDK (MIT), and Ollama (MIT), and describes the components as verified. The supplied report does not provide pinned versions, license-file links, dates, or maintenance evidence. Perplexity also mentions Vercel AI SDK and rejects Open WebUI without enough license detail in the summary. Claude deliberately lists no components as verified.

**Decision:** no component is approved based on the reports alone. Verify the exact repository, version/tag, LICENSE file, maintenance activity, and browser/provider compatibility before adding dependencies. Grok's “OpenAI-compatible clients” row is a category, not a specific repository and cannot be treated as a verified component.

## 5. Resource Governor: agree on simplicity, tighten the safety claim

Grok proposes `max_runs_per_day`, `timeout_minutes`, `max_agent_steps`, `max_tokens_per_task`, concurrency=1, cancellation, and one retry. Claude proposes similar per-task limits. Perplexity proposes an initial governor check plus timeout and concurrency.

The controls are directionally useful, but a workflow's first step runs only after runner allocation; local counters can race; token limits need actual provider usage measurement; and cancellation cannot reverse work already performed.

**Decision:** keep the Governor small, but describe it as a usage-control mechanism, not a guaranteed hard financial cap. For any permitted workflow: strict timeout, serialized concurrency, maximum steps/retries, preflight quota check, and post-run usage record.

## 6. Updated decision log

| Area | Current decision |
|---|---|
| Product verdict | Revise |
| Fast chat | Direct official provider streaming with BYOK where browser access is supported; otherwise user-controlled proxy/local process |
| Authentication | GitHub App with minimal permissions; tiny token broker preferred for a web app if free and acceptable |
| GitHub Actions | Software-project CI/CD only pending written clarification; not approved as general-purpose agent runtime |
| General background tasks | User-controlled local/device execution or independently user-operated compute outside Actions |
| Memory | Small Markdown/JSON files in a private user repository; no secrets or sensitive content |
| Resource Governor | Bounded execution and measured usage; no promise of a hard spend ceiling |
| Dependencies | No adoption until exact licenses and maintenance evidence are verified |
| Browser automation / enterprise | Later |

## 7. Does the recommendation change?

No. The verdict remains **Revise**. Grok reinforces the policy risk and overall direction. The main new finding is an inconsistency between Grok's stated policy mitigation and its proposed Actions-based async MVP workflow. That must be resolved before implementation.

## Build now / Defer / First executable task

- **Build now:** prove one official provider's browser streaming path with a user-supplied key, including CORS, cancellation, error handling, and checks that the key never enters public source, logs, or repository history.
- **Defer:** general-purpose Actions execution, broad multi-provider orchestration, browser automation, and enterprise features.
- **First executable task:** build a minimal static chat spike for one provider. Separately, test GitHub App authorization/token exchange as a bounded auth spike. Do not combine these with a general-purpose Actions runner until the policy boundary is resolved.
