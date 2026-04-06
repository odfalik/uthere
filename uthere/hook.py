"""Claude Code Stop hook — checks if the user is present before handing back control.

Flow:
  1. Agent finishes a response and is about to stop.
  2. This hook fires, captures from camera, runs face detection.
  3. If user IS present (or camera fails): allow the stop (no output).
  4. If user is NOT present: block the stop with a message so the agent
     can keep working autonomously.

Anti-loop safeguard:
  After blocking once, a cooldown file is written. If the agent tries to
  stop again within COOLDOWN_SECONDS, the stop is allowed unconditionally
  to prevent infinite block cycles.
"""

import json
import sys
import tempfile
import time
from pathlib import Path

COOLDOWN_FILE = Path(tempfile.gettempdir()) / "uthere_hook_cooldown"
COOLDOWN_SECONDS = 60


def main() -> None:
    # Anti-loop: if we blocked recently, allow this stop
    if COOLDOWN_FILE.exists():
        try:
            last_block = float(COOLDOWN_FILE.read_text().strip())
            if time.time() - last_block < COOLDOWN_SECONDS:
                # Recently blocked — allow stop, clear cooldown
                COOLDOWN_FILE.unlink(missing_ok=True)
                return
        except (ValueError, OSError):
            COOLDOWN_FILE.unlink(missing_ok=True)

    # Import here so camera only initializes when needed
    from uthere.detect import detect_user_presence

    try:
        present = detect_user_presence()
    except Exception:
        # Camera issue — don't block the agent
        return

    if present:
        # User is here — allow stop
        COOLDOWN_FILE.unlink(missing_ok=True)
        return

    # User not present — block stop, record cooldown
    COOLDOWN_FILE.write_text(str(time.time()))
    output = {
        "decision": "block",
        "reason": (
            "The user is not at their computer right now (no face detected via webcam). "
            "If you have remaining work to do on the current task, keep going. "
            "If you're blocked and truly need user input, send them a DM on Slack to get their attention. "
            "If you've completed everything, you may stop."
        ),
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
