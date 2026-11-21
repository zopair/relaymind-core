# InstaPro — Independent Multi-Model Architecture Review

## Mission
Review the proposed InstaPro platform as a practical, zero-company-compute, GitHub-native AI agent platform. The product should let each user connect their own GitHub account and own repository, supply their own provider credentials where needed, and use their own compute/provider quotas transparently.

## Product requirements
1. Fast conversational interface with streaming responses.
2. Asynchronous agents for longer tasks, orchestrated through the user's GitHub repository and GitHub Actions.
3. GitHub-only sign-in for the MVP.
4. User-owned repository and infrastructure (BYOC); no mandatory company-funded inference or compute.
5. Optional routing to Claude, Gemini, Grok, Perplexity, and open-source/local models, subject to official APIs and user-provided credentials.
6. Browser automation and tool execution with explicit permissions and auditable runs.
7. Persistent memory and task artifacts stored in the user's repository or GitHub-native storage.
8. Resource Governor for Actions minutes, API quotas, concurrency, storage, artifacts, and runaway-task prevention.
9. Mobile-first UI; clear status, logs, approvals, and cost/usage visibility.

## Questions for the reviewer
A. Propose the simplest viable architecture and data flow. Separate fast chat/inference from asynchronous execution.
B. Identify fatal flaws, hidden costs, GitHub policy/terms risks, rate-limit issues, and operational bottlenecks.
C. Explain exactly which GitHub-native capabilities can be used, their limitations, and which workloads need external providers or self-hosted runners.
D. Compare secure GitHub OAuth / GitHub App installation / fine-grained PAT approaches. Never recommend placing secrets in browser code or public files.
E. Recommend practical provider adapters for Claude, Gemini, Grok, Perplexity, and open-source models. Distinguish official APIs from unsupported workarounds.
F. Identify mature open-source GitHub repositories that can be reused. Include repository URL, license, maintenance signals, fit, and integration cost. Do not invent repositories or licenses.
G. Design a minimal Resource Governor and explain how to prevent unbounded spend, Actions usage, loops, and concurrency.
H. Give a phased MVP roadmap that avoids over-engineering.

## Required response format
1. Executive verdict (build / revise / reject).
2. Recommended architecture (Mermaid diagram).
3. Critical risks and mitigations, ranked by severity.
4. GitHub-native capability matrix with limits and caveats.
5. Verified open-source components (URLs + exact licenses).
6. MVP roadmap (small, testable phases).
7. Decisions that must be made before implementation.
8. Explicit assumptions and unknowns. Separate verified facts from inference.

## Constraints
- Prefer free and open-source components and GitHub-native features.
- No paid infrastructure requirement for the company.
- Do not claim GitHub Actions, Codespaces, hosted runners, or model APIs are unlimited or universally free.
- Do not propose evading provider terms, hiding usage, scraping private interfaces, or sharing credentials.
- Optimize for a lean proof of concept that can later be customized for enterprise buyers.
- Be candid. Challenge the premise where necessary.

## Review target
This is a research brief only. Do not modify production code or merge changes.
