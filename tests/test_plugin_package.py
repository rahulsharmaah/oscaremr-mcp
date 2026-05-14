import json
import subprocess
from pathlib import Path


def test_codex_plugin_manifest_is_present_and_current():
    manifest_path = Path(".codex-plugin/plugin.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["name"] == "oscar-db-mcp"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert manifest["skills"] == "./skills/"
    assert "OSCAR EMR MariaDB/MySQL" in manifest["description"]
    assert "Agentic Clinic" not in json.dumps(manifest)


def test_codex_local_plugin_installer_is_documented():
    readme = Path("README.md").read_text(encoding="utf-8")
    codex_docs = Path("docs/clients/codex.md").read_text(encoding="utf-8")

    assert "install_codex_local_plugin.ps1" in readme
    assert "install_codex_local_plugin.ps1" in codex_docs


def test_one_click_platform_installers_are_documented():
    readme = Path("README.md").read_text(encoding="utf-8")
    one_click_docs = Path("docs/one-click-install.md").read_text(encoding="utf-8")
    codex_docs = Path("docs/clients/codex.md").read_text(encoding="utf-8")
    cursor_docs = Path("docs/clients/cursor.md").read_text(encoding="utf-8")

    assert "Install Oscar EMR MCP.cmd" in readme
    assert "Install Oscar EMR MCP.cmd" in one_click_docs
    assert "install_oscar_emr_mcp_unix.sh" in readme
    assert "install_oscar_emr_mcp_unix.sh" in one_click_docs
    assert "install_codex_local_plugin.py" in codex_docs
    assert "install_cursor_mcp.py" in cursor_docs
    assert "Codex Cloud" in one_click_docs
    assert "remote MCP gateway" in one_click_docs


def test_cursor_deeplink_generator_outputs_install_link():
    result = subprocess.run(
        ["python", "scripts/generate_cursor_deeplink.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    link = result.stdout.strip()
    assert link.startswith("cursor://anysphere.cursor-deeplink/mcp/install?")
    assert "name=oscar-emr-mcp" in link
    assert "config=" in link
