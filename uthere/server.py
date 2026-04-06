"""MCP server exposing a single tool: is_user_present."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("uthere")


@mcp.tool()
def is_user_present() -> dict:
    """Check if the user is sitting at their computer by detecting a face via the webcam.

    Returns {"present": true/false} with an explanatory message.
    If the camera cannot be accessed, returns an error message.
    """
    from uthere.detect import detect_user_presence

    try:
        present = detect_user_presence()
        return {
            "present": present,
            "message": (
                "User is at their computer."
                if present
                else "No face detected — user appears to be away. If you need their input, try reaching them on Slack."
            ),
        }
    except RuntimeError as e:
        return {
            "present": None,
            "error": str(e),
            "message": "Could not determine presence — camera unavailable.",
        }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
