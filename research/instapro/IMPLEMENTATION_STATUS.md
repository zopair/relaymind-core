# InstaPro Implementation Status

Date: 2026-11-21
Working branch: `feat/instapro-user-mvp`
Base: `research/instapro-multi-model-review`

## Current verified state

- This repository currently contains the RelayMind short-video generation engine (Python), its GitHub Actions validation workflow, a client workflow template, and the InstaPro research reports.
- There is no web application, chat interface, authentication flow, provider adapter, or user-facing task dashboard in this repository.
- The existing Actions workflow is a validation workflow for the video engine. The client workflow template uses Actions to generate short videos; it must not be repurposed as InstaPro's general-purpose agent runtime.
- The research decision remains: fast chat must be independent of GitHub Actions; general-purpose asynchronous execution through Actions is not approved pending policy clarification.

## Implementation sequence

1. Preserve the existing RelayMind engine and research reports.
2. Add the InstaPro user-facing web app as an isolated product surface, following the previously supplied visual reference; do not expose GitHub or infrastructure concepts in the user experience.
3. Prove one real provider chat path with user-controlled credentials, streaming where officially supported, cancellation, and safe error handling.
4. Add a single bounded background-task path outside GitHub Actions only after selecting a compliant user-controlled execution model.
5. Add memory and artifact history after the first real chat/task flow works.

## First acceptance gate

The first user-facing build is accepted only when:
- it follows the supplied InstaPro visual reference rather than inventing a new product direction;
- a non-technical user can open it and start a conversation without seeing repository, workflow, branch, or runner terminology;
- the UI clearly distinguishes a real provider response from any local/demo state;
- no API key or secret is embedded in public source or browser-delivered configuration.

## Current blocker

The visual reference image is not present in this repository's files, and no existing InstaPro frontend is present to extend. Do not claim visual parity or fabricate details from an unavailable image. Continue implementation against the confirmed product requirements while preserving this explicit visual acceptance gate.
