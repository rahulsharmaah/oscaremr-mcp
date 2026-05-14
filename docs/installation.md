# Installation

Clone the project into any location that works for your environment.

## Guided Setup

On Windows, double-click:

```text
Install Oscar EMR MCP.cmd
```

On macOS/Linux, run:

```bash
./scripts/install_oscar_emr_mcp_unix.sh
```

The guided setup installs dependencies, opens the database wizard, prepares Codex Desktop, and registers Cursor when a database config exists.

## Windows PowerShell

```powershell
git clone https://github.com/rahulsharmaah/oscaremr-mcp.git
cd oscaremr-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## macOS / Linux

```bash
git clone https://github.com/rahulsharmaah/oscaremr-mcp.git
cd oscaremr-mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Verify the Install

Run the unit tests:

```powershell
pytest
```

Run the server module:

```powershell
python -m oscar_db_mcp.server
```

The server uses stdio for MCP traffic. If it appears to wait quietly, that is expected.

## Command-Line Entry Points

After installation, these commands are available inside the virtual environment:

```powershell
oscar-db-mcp
oscar-db-mcp-configure --interactive
```
