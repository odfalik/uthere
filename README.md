# uthere

Camera-based presence detection for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Uses your webcam to check if you're sitting at your computer.

Two components:

1. **MCP server** -- exposes an `is_user_present` tool that Claude can call anytime to check if you're there
2. **Stop hook** -- automatically keeps Claude working when you step away, so it doesn't stop and wait for input from an empty chair

Uses [MediaPipe BlazeFace](https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector) for fast, lightweight face detection. Works well with glasses, varied lighting, and different angles. The model (~200KB) is downloaded automatically on first run.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/odfalik/uthere.git
cd uthere
uv sync
```

### Camera permissions

On macOS, your terminal app needs camera access. Go to **System Settings > Privacy & Security > Camera** and enable it for your terminal (Terminal, iTerm2, etc).

## Setup

Add either or both of the following to your Claude Code settings file (`~/.claude/settings.json`).

### MCP server

Gives Claude a tool it can call to check if you're at your desk.

```json
{
  "mcpServers": {
    "uthere": {
      "command": "uv",
      "args": ["--directory", "/path/to/uthere", "run", "python", "-m", "uthere.server"]
    }
  }
}
```

### Stop hook

Prevents Claude from stopping when you're away. If Claude finishes a response and no face is detected, it gets a message telling it to keep going. A 60-second cooldown prevents infinite loops.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv --directory /path/to/uthere run python -m uthere.hook",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Configuration

All configuration is through environment variables. Set them in your shell profile or in Claude Code's `env` settings.

| Variable | Default | Description |
|---|---|---|
| `UTHERE_AWAY_MESSAGE` | `"No face detected. User appears to be away..."` | MCP tool message when no face is detected |
| `UTHERE_PRESENT_MESSAGE` | `"User is at their computer."` | MCP tool message when face is detected |
| `UTHERE_HOOK_MESSAGE` | `"The user is not at their computer right now..."` | Message sent to the agent when the stop hook blocks |
| `UTHERE_COOLDOWN_SECONDS` | `60` | Seconds before the stop hook can block again |

Example using Claude Code's env settings:

```json
{
  "env": {
    "UTHERE_AWAY_MESSAGE": "User is away. Send them a message on Discord.",
    "UTHERE_HOOK_MESSAGE": "User is AFK. Keep working, ping them on Discord if stuck."
  }
}
```

## How it works

1. Opens the webcam via OpenCV
2. Takes a few warmup frames (lets auto-exposure settle)
3. Checks 3 consecutive frames with BlazeFace face detection
4. Returns `true` if a face is found in any frame

The whole check takes about 1-2 seconds. The camera is released immediately after each check.

## License

MIT
