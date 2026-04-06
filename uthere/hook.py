"""Claude Code Stop hook -- checks if the user is present before handing back control.

Flow:
  1. Agent finishes a response and is about to stop.
  2. This hook fires, captures from camera, runs face detection.
  3. If user IS present (or camera fails): allow the stop (no output).
  4. If user is NOT present: block the stop with a message so the agent
     can keep working autonomously.

Anti-loop safeguard:
  A flag file is written when the hook blocks. On the next invocation, if
  the flag exists, the hook allows the stop and removes the flag. This
  gives the agent exactly one nudge per cycle.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

BLOCK_FLAG = Path(tempfile.gettempdir()) / "uthere_hook_blocked"

HOOK_BLOCK_MESSAGE = os.environ.get(
    "UTHERE_HOOK_MESSAGE",
    "The user is not at their computer right now (no face detected via webcam). "
    "If you have remaining work to do on the current task, keep going. "
    "If you're blocked and truly need user input, send them a DM on Slack to get their attention. "
    "If you've completed everything, you may stop.",
)


def main() -> None:
    # Anti-loop: if we already blocked once, let the agent stop
    if BLOCK_FLAG.exists():
        BLOCK_FLAG.unlink(missing_ok=True)
        return

    # Import here so camera only initializes when needed
    from uthere.detect import detect_user_presence

    try:
        present = detect_user_presence()
    except Exception:
        # Camera issue -- don't block the agent
        return

    if present:
        return

    # User not present -- block stop, set flag
    BLOCK_FLAG.touch()
    output = {
        "decision": "block",
        "reason": HOOK_BLOCK_MESSAGE,
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
