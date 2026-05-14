import json
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
