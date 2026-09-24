# zoom-ai-copilot

macOS-native personal AI copilot for Zoom meetings. It captures remote participants' audio in real time, generates contextual response candidates using LLMs, synthesizes responses in the user's cloned voice, and plays back speech into Zoom via virtual audio routing (Loopback).

> [!IMPORTANT]
> **Safety First / Human-in-the-Loop:**
> In this MVP, automatic speech generation is strictly disabled by default (`AUTO_SPEAK=false`). The AI will only output voice to Zoom when the user explicitly reviews the suggested response and presses the **Speak** button.

---

## Architecture

### System & Audio Routing Overview

```text
┌──────────────────────────────────────────────────────────┐
│                   Zoom Remote Participant                │
└────────────────────────────┬─────────────────────────────┘
                             │ Audio output
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Loopback: "Zoom Capture" Device             │
└────────────────────────────┬─────────────────────────────┘
                             │ Virtual Audio Input
                             ▼
┌──────────────────────────────────────────────────────────┐
│                     zoom-ai-copilot                      │
│                                                          │
│  [Speech-to-Text] ──► [LLM Generator] ──► [GUI Review]   │
│   (Mock / Realtime)    (Mock / OpenAI)     (PySide6)     │
│                                               │          │
│                                        [User clicks]     │
│                                           [Speak]        │
│                                               │          │
│                                               ▼          │
│                                      [Text-to-Speech]    │
│                                    (Mock / ElevenLabs)   │
└────────────────────────────┬─────────────────────────────┘
                             │ Virtual Audio Output
                             ▼
Physical Microphone ─────────┐
                             ├──► Loopback: "Zoom AI Mic" ──► Zoom Microphone Input
AI TTS Output ───────────────┘
```

### Feedback Loop Prevention

```text
       ┌────────────────────────┐
       │   Zoom Remote Audio    │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Loopback Zoom Capture │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │     zoom-ai-copilot    │
       │           STT          │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │      LLM Response      │
       └───────────┬────────────┘
                   │
                   ▼ (User clicks Speak)
       ┌────────────────────────┐
       │     TTS Synthesis      │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Loopback Zoom AI Mic  │───────► Zoom Mic Input (Remote Participants hear this)
       └────────────────────────┘
                   │
                   X (NO FEEDBACK: Zoom AI Mic is strictly separated from Zoom Capture)
```

Audio I/O uses dedicated input and output devices. The AI voice output is fed exclusively to the virtual microphone device (`Zoom AI Mic`) and is never routed back into the STT capture device (`Zoom Capture`).

---

## Features

- **Real-Time Audio Capture & Transcription:** Ingests remote audio streams via virtual audio devices. Pluggable architecture supports Mock STT and OpenAI Realtime Transcription.
- **Context-Aware Response Generation:** Generates direct, concise spoken Japanese answers tailored for meetings using OpenAI models or Mock LLM.
- **Cloned Voice Synthesis:** Synthesizes speech via ElevenLabs with personalized Voice IDs (or Mock TTS for testing).
- **Human-in-the-Loop Safety:** Never speaks automatically without explicit user confirmation.
- **Immediate Audio Stop:** Instantly halts TTS audio output at any time with the `Stop` button.
- **Response Regeneration:** Re-queries the LLM with latest context if the suggestion needs refinement.
- **Modular & Pluggable Architecture:** Independently toggle STT, LLM, and TTS providers between `mock` and real APIs.
- **Zero-Secret Logging:** Strict privacy controls ensure API keys, voice IDs, and transcript payloads are never leaked into logs.

---

## Requirements

- **OS:** macOS 14+ (Apple Silicon recommended)
- **Python:** 3.12+
- **Package Manager:** [uv](https://docs.astral.sh/uv/) (v0.5+)
- **Virtual Audio Driver:** [Rogue Amoeba Loopback](https://rogueamoeba.com/loopback/) (recommended)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/moruku36/zoom-ai-copilot.git
   cd zoom-ai-copilot
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

---

## Configuration

Edit `.env` to configure providers and credentials:

```dotenv
# Provider Selection (mock | openai | elevenlabs)
STT_PROVIDER=mock
LLM_PROVIDER=mock
TTS_PROVIDER=mock

# OpenAI Settings (required if LLM_PROVIDER=openai or STT_PROVIDER=openai)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_LLM_MODEL=gpt-4o-mini
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview

# ElevenLabs Settings (required if TTS_PROVIDER=elevenlabs)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_elevenlabs_voice_id_here
ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# Audio Device Settings (optional: names or partial names)
AUDIO_INPUT_DEVICE=
AUDIO_OUTPUT_DEVICE=

# Safety Settings
AUTO_SPEAK=false
PHYSICAL_MIC_PASSTHROUGH=true
```

---

## Mock Mode

You can run and test the complete pipeline **without any API keys or network access**:

1. Ensure providers are set to `mock` in `.env`:
   ```dotenv
   STT_PROVIDER=mock
   LLM_PROVIDER=mock
   TTS_PROVIDER=mock
   ```
2. Start the application:
   ```bash
   uv run python -m zoom_ai_copilot.main
   ```
3. The UI will simulate transcription, generate a mocked response, and allow you to test `Speak`, `Stop`, and `Regenerate` controls.

---

## OpenAI Setup

1. Obtain an API key from [OpenAI Platform](https://platform.openai.com/).
2. Set in `.env`:
   ```dotenv
   OPENAI_API_KEY=sk-...
   LLM_PROVIDER=openai
   ```

---

## ElevenLabs Setup

1. Obtain an API key and cloned Voice ID from [ElevenLabs](https://elevenlabs.io/).
2. Set in `.env`:
   ```dotenv
   ELEVENLABS_API_KEY=your_key
   ELEVENLABS_VOICE_ID=your_voice_id
   TTS_PROVIDER=elevenlabs
   ```

---

## Loopback Setup

To connect Zoom and zoom-ai-copilot on macOS using Rogue Amoeba Loopback:

1. **Create Virtual Device 1: `Zoom Capture`**
   - Source: Add `zoom.us` as an audio source.
   - Monitors: None (or headphones if you want to monitor directly).
   - In `zoom-ai-copilot`, select `Zoom Capture` as the **Audio Input**.

2. **Create Virtual Device 2: `Zoom AI Mic`**
   - Source: Add your physical microphone (Pass-through) + Pass-Thru channel for app audio.
   - In `zoom-ai-copilot`, select `Zoom AI Mic` as the **Audio Output**.
   - In Zoom audio settings, set the **Microphone** to `Zoom AI Mic`.

---

## Running

Launch the desktop GUI:

```bash
uv run python -m zoom_ai_copilot.main
```

Or using the installed entrypoint:

```bash
uv run zoom-ai-copilot
```

---

## Testing

Run unit and integration tests:

```bash
uv run pytest
```

Run linter:

```bash
uv run ruff check .
```

---

## Security Notes

- API keys (`OPENAI_API_KEY`, `ELEVENLABS_API_KEY`) and Voice IDs must **never** be committed to Git.
- `.env` is listed in `.gitignore`.
- Secrets are masked in logs and application state dumps.

## Privacy Notes

- Transcripts and audio buffers are processed entirely in-memory and are discarded when the application closes.
- No audio or text logs are uploaded to any third-party analytics or persistent databases.

---

## Limitations

- The initial MVP is designed for macOS (Apple Silicon).
- Automatic question detection and automatic interruption (barge-in) are not implemented in the MVP.
- Offline speech recognition and local LLM execution require future extensions.

---

## Future Work

- [ ] Push-to-talk keyboard shortcut
- [ ] Automatic question detection
- [ ] Streaming TTS (low-latency chunked audio playback)
- [ ] OpenAI Realtime speech-to-speech adapter
- [ ] Local Whisper transcription support
- [ ] Local LLM inference (e.g. Ollama / MLX)
- [ ] Speaker diarization
- [ ] Meeting context import (agenda, documents)
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] User profile / preferred speaking style customization
- [ ] Automatic response suggestion trigger
- [ ] Voice interruption / barge-in handling
- [ ] macOS Menu Bar background app mode
