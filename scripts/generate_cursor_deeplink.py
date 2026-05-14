from __future__ import annotations

import base64
import json
from urllib.parse import quote


NAME = "oscar-emr-mcp"
CONFIG = {
    "type": "stdio",
    "command": "oscar-db-mcp",
    "args": [],
    "envFile": "${userHome}${/}.oscaremr-mcp${/}.env",
}


def main() -> None:
    payload = json.dumps(CONFIG, separators=(",", ":")).encode("utf-8")
    encoded = base64.b64encode(payload).decode("ascii")
    print(f"cursor://anysphere.cursor-deeplink/mcp/install?name={NAME}&config={quote(encoded)}")


if __name__ == "__main__":
    main()
