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


## Multi-model collaboration protocol (mandatory)
This review is a shared workspace for several independent AI reviewers (for example Claude, Gemini, Grok, Perplexity, and ChatGPT). The human coordinator may paste each model's response into this same repository/branch so every reviewer can inspect the others' work.

### Instructions to every reviewer
1. Start by writing your own independent review. Do not simply agree with earlier reviewers.
2. Read the other reviewers' reports in this folder before writing your final position.
3. Explicitly identify:
   - points where you agree, with reasons;
   - points where you disagree, with evidence or a concrete technical argument;
   - important omissions or risks nobody has raised;
   - claims that need verification and the source needed to verify them.
4. Challenge recommendations constructively. Do not manufacture consensus. If evidence is insufficient, label the point unresolved.
5. After reviewing others, publish a short **Round 2 — Cross-Review** section in your own report. State whether your original recommendation changed and why.
6. If you cannot access repository files other than this brief, say so clearly. Do not pretend to have read other models' reports. Ask the coordinator to provide the report links or pasted contents.
7. Do not edit or overwrite another model's report. Create a separate file named `reports/<model-name>.md`; use a recognizable provider/model label in the filename.
8. Keep all credentials, API keys, OAuth secrets, and private user data out of reports and commits.

### Shared discussion sequence
- Round 1: each model independently reviews this brief and commits its report under `reports/`.
- Round 2: each model reads the other available reports and adds a cross-review section to its own report (or creates `reports/<model-name>-cross-review.md` if editing is not possible).
- Synthesis: the coordinator asks ChatGPT to compare all reports, identify consensus and disagreements, verify factual claims, and produce a decision log. No model is treated as the authority by default.

### Suggested report header
- Provider/model:
- Review date:
- Evidence links:
- Executive verdict:
- Confidence (high / medium / low):
- Key assumptions:


## Mandatory execution discipline — practical research only

This section overrides any tendency toward open-ended debate or unnecessary technical expansion. The goal is a working MVP that obeys the constraints below, not the most elaborate architecture.

### Non-negotiable rules for every reviewer
1. **No debate without a decision:** raise an objection only when it changes feasibility, cost, performance, policy compliance, or implementation. State the evidence, impact, and a practical resolution briefly.
2. **No over-engineering:** do not add services, agents, frameworks, databases, abstraction layers, or infrastructure unless a demonstrated MVP requirement needs them. Prefer the smallest working design.
3. **Respect the project constraints:** GitHub-first; free and open-source where feasible; no mandatory company-funded hosting, inference, or compute; user-owned GitHub repository, credentials, quotas, and resources (BYOC/BYOK). Be explicit about unavoidable limits and costs.
4. **Research for implementation:** prioritize maintained, real repositories and official documentation. For each proposed component, provide its exact URL, license, maintenance evidence, what it replaces, integration effort, and a concrete test to prove it works. Never invent verification.
5. **Every recommendation must be actionable:** describe the smallest implementation step, its dependency, acceptance check, and fallback if blocked. Prefer one recommended option over a long list.
6. **Replace blockers with workable alternatives:** explain the constraint briefly, then propose the simplest compliant workaround. Do not stop at criticism.
7. **Keep MVP scope tight:** label non-essential capabilities as “Later”; do not let them expand the first deliverable.
8. **Separate facts from assumptions:** cite official evidence for current GitHub/provider limits, pricing, policies, and API availability. Mark anything not verified as unverified.
9. **Avoid repeated analysis:** do not restate points already covered unless adding new evidence or changing the decision. Keep the report concise and decision-oriented.

### Required practical output
For each major recommendation, use this compact format:
- **Decision:** one clear choice.
- **Evidence:** official source or real repository, with license where applicable.
- **Implementation:** smallest concrete step.
- **Validation:** a reproducible test and expected result.
- **Constraint/fallback:** relevant cost, quota, policy limitation, or simpler alternative.

End with:
- **Build now:** the smallest useful MVP scope.
- **Defer:** features that are not required to prove the MVP.
- **First executable task:** one specific task that can be started immediately.

A technically impressive proposal that violates the project's cost, ownership, simplicity, or execution constraints is not an acceptable recommendation.
