"""Claude Code Stop hook -- checks if the user is present before handing back control.

Flow:
  1. Agent finishes a response and is about to stop.
  2. This hook fires, captures from camera, runs face detection.
  3. If user IS present (or camera fails): allow the stop (no output).
  4. If user is NOT present: block the stop with a message so the agent
     can keep working autonomously.

Anti-loop safeguard:
  The hook reads the last assistant message from stdin. If the agent was
  already told the user is away and is trying to stop again, it has nothing
  left to do -- let it stop. No temp files, fully stateless.
"""

import json
import os
import sys

# Sentinel substring used to detect if we already blocked once this cycle.
# If the block message appears in the agent's last response, it was already
# nudged and chose to stop anyway -- let it through.
_BLOCK_SENTINEL = "no face detected via webcam"

HOOK_BLOCK_MESSAGE = os.environ.get(
    "UTHERE_HOOK_MESSAGE",
    "The user is not at their computer right now (no face detected via webcam). "
    "If you have remaining work to do on the current task, keep going. "
    "If you're blocked and truly need user input, send them a DM on Slack to get their attention. "
    "If you've completed everything, you may stop.",
)


def main() -> None:
    # Read the hook payload from stdin
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return

    # Anti-loop: if the agent's last message already references our block
    # message, it was already nudged and chose to stop -- let it through.
    last_message = payload.get("last_assistant_message", "")
    if _BLOCK_SENTINEL in last_message.lower():
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

    # User not present -- block stop
    output = {
        "decision": "block",
        "reason": HOOK_BLOCK_MESSAGE,
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
