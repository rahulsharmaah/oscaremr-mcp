#!/usr/bin/env bash
set -euo pipefail

skip_database_wizard=0
skip_codex=0
skip_cursor=0

for arg in "$@"; do
  case "$arg" in
    --skip-database-wizard) skip_database_wizard=1 ;;
    --skip-codex) skip_codex=1 ;;
    --skip-cursor) skip_cursor=1 ;;
    -h|--help)
      cat <<'HELP'
Oscar EMR MCP setup for macOS and Linux

Usage:
  ./scripts/install_oscar_emr_mcp_unix.sh [options]

Options:
  --skip-database-wizard  Install without prompting for database settings.
  --skip-codex            Do not create the Codex local marketplace package.
  --skip-cursor           Do not update Cursor's global MCP config.
HELP
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
data_home="${XDG_DATA_HOME:-"$HOME/.local/share"}"
install_root="$data_home/oscaremr-mcp"
venv_dir="$install_root/.venv"
python="$venv_dir/bin/python"
env_file="$HOME/.oscaremr-mcp/.env"

echo "Oscar EMR MCP setup"
echo "===================="
echo

mkdir -p "$install_root"

if [[ ! -x "$python" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    base_python="python3"
  elif command -v python >/dev/null 2>&1; then
    base_python="python"
  else
    echo "Python 3.11 or newer was not found. Install Python, then run this installer again." >&2
    exit 1
  fi

  echo "Creating Python virtual environment..."
  "$base_python" -m venv "$venv_dir"
fi

echo "Installing Oscar EMR MCP dependencies..."
"$python" -m pip install --upgrade pip
"$python" -m pip install "$repo_root"

if [[ "$skip_database_wizard" -eq 0 ]]; then
  echo
  echo "Configuring OSCAR EMR database connection..."
  "$python" -m oscar_db_mcp.configure --interactive --env-path "$env_file"
elif [[ ! -f "$env_file" ]]; then
  echo "Database wizard skipped and no user env file exists yet."
  echo "Run: oscar-db-mcp-configure --interactive --env-path \"$env_file\""
fi

if [[ "$skip_codex" -eq 0 ]]; then
  echo
  echo "Preparing Codex local plugin marketplace..."
  "$python" "$repo_root/scripts/install_codex_local_plugin.py" \
    --python-path "$python" \
    --server-cwd "$install_root"
fi

if [[ "$skip_cursor" -eq 0 ]]; then
  if [[ -f "$env_file" ]]; then
    echo
    echo "Installing Cursor MCP configuration..."
    "$python" "$repo_root/scripts/install_cursor_mcp.py" \
      --python-path "$python" \
      --env-file "$env_file"
  else
    echo "Skipping Cursor registration because the database env file is missing."
  fi
fi

echo
echo "Setup complete."
echo
echo "Next steps:"
echo "- Restart Codex, open Plugins, and install Oscar EMR MCP from Local Plugins."
echo "- Restart Cursor or reload MCP servers from Cursor Settings > MCP."
echo "- To verify the MCP stream, run: oscar-db-mcp"
