# RelayMind Core

![CDN](https://img.shields.io/badge/architecture-CDN--first-111827) ![Python](https://img.shields.io/badge/python-3.11-blue) ![Cost](https://img.shields.io/badge/stack-free%20tiers%20%2B%20open%20source-success)

Centralized engine for turning a topic into a vertical short video. Client repositories download the engine through jsDelivr and run it on their own GitHub Actions runners. The local model runtime and weights are cached per client repository after first download.

## Architecture

```mermaid
flowchart TD
 A[Manual workflow_dispatch] --> B[jsDelivr CDN download]
 B --> C[Prompt enhancer]
 C --> D{GitHub Models}
 D -->|Available| E[Structured script]
 D -->|Unavailable| F[Rule-based fallback]
 E --> G[Media factory]
 F --> G
 G --> H[edge-tts]
 G --> I[Pollinations images]
 I -->|Unavailable| J[Pillow gradient frames]
 H --> K[ffmpeg + captions]
 J --> K
 K --> L[MP4 + JSON metadata]
 L --> M[Optional Telegram delivery]
```

## Centralized CDN Engine

Client workflow template: [templates/client_workflow.yml](templates/client_workflow.yml). It downloads `runner.py` and the engine modules from `https://cdn.jsdelivr.net/gh/zopair/relaymind-core@main/`. Client execution is local to the client Actions runner. CDN delivery avoids cloning this repository in client workflows; it does not eliminate upstream/CDN network traffic.

## Zero-Cost / Open-Source Stack

- GitHub Actions, local llama.cpp inference and the Apache-2.0 Qwen2.5-0.5B-Instruct Q4_K_M model.
- edge-tts, Pollinations public image endpoint with Pillow fallback, and ffmpeg.
- `edge-tts` for speech synthesis, relying on a public Edge speech service without a guaranteed free-tier SLA.
- Pollinations public image endpoint with Pillow fallback.
- ffmpeg and Python open-source packages.
- Optional Telegram Bot API delivery.

**Important provider change (verified 2026-11-21):** GitHub Models was fully retired on July 30, 2026, including its inference API. It now returns no usable model completion. RelayMind therefore uses local CPU inference through the MIT-licensed llama.cpp runtime and the Apache-2.0 Qwen2.5-0.5B-Instruct Q4_K_M GGUF model. Both runtime and model downloads are SHA-256 verified and cached by Actions. No hosted LLM API key is needed.

## Minute-Saving Protocol

- `workflow_dispatch` only; no idle cron.
- Concurrency lock; `timeout-minutes: 4`.
- pip cache, bounded retries and network timeouts.
- Four visual scenes and one ffmpeg render.
- No server, database, paid API or always-on worker.

Four minutes is a hard job ceiling, not a guarantee of successful 1080×1920 rendering for every topic. Hosted runner load, external service latency and narration length affect runtime.

## Setup

Copy `templates/client_workflow.yml` to a client repository as `.github/workflows/relaymind.yml`. Run it manually and enter a topic. Optionally configure repository secrets `TG_TOKEN` and `TG_CHAT_ID`.

## Environment

| Variable | Purpose |
|---|---|
| `TOPIC` | Required user idea |
| `LANG` | `auto`, `ar`, or `en` |
| `RELAYMIND_LLAMA_CLI` | Path to the verified local llama.cpp CLI binary |
| `RELAYMIND_MODEL_PATH` | Path to the verified Qwen GGUF model |
| `TG_TOKEN`, `TG_CHAT_ID` | Optional Telegram delivery |
| `WA_PHONE` | Reserved only; WhatsApp delivery is not implemented |

A phone number alone cannot send WhatsApp messages. It requires an authorized WhatsApp Business API integration and credentials. This engine does not claim to send WhatsApp messages.

## Outputs

`output/final_short.mp4`, `output/metadata.json`, four scene images and `output/voiceover.mp3`.

## Proof of Concept & Enterprise Customization Readiness

**Status:** offline rendering and the live end-to-end fallback path have passed GitHub Actions validation. Local Qwen inference is included; live model output is validated separately from the offline renderer. External image/TTS availability remains best-effort; no SLA or guaranteed sub-four-minute completion is claimed.

**Changelog:** initial CDN engine, structured prompt fallback, media fallbacks, resolver, Telegram delivery and manual workflow template.

## Intellectual Property & Authorship

Copyright © Aly Hussein Zopair (علي حسين زبير ALY HUSSEIN ZOPAIR). All rights reserved unless a separate license or written agreement states otherwise.
