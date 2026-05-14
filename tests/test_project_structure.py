from pathlib import Path


def test_emr_tools_are_split_by_feature_area():
    emr_dir = Path("src/oscar_db_mcp/emr")
    expected_modules = {
        "base.py",
        "patients.py",
        "scheduling.py",
        "medications.py",
        "clinical.py",
        "workflow.py",
        "records.py",
        "billing.py",
    }

    assert expected_modules.issubset({path.name for path in emr_dir.glob("*.py")})


def test_domain_module_stays_as_compatibility_shim():
    source = Path("src/oscar_db_mcp/domain.py").read_text(encoding="utf-8")

    assert "from oscar_db_mcp.emr import OscarEmrReadTools" in source
    assert "def find_patients" not in source
    assert len(source.splitlines()) <= 10
