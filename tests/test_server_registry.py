import ast
from pathlib import Path


def test_server_exposes_expanded_tool_catalog():
    source = Path("src/oscar_db_mcp/server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    tool_names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "tool"
            ):
                tool_names.append(node.name)

    assert len(tool_names) >= 55
    for expected in [
        "find_patients",
        "get_patient_summary",
        "list_patient_medications",
        "list_patient_labs",
        "search_billing_codes",
        "audit_patient_access_log",
    ]:
        assert expected in tool_names
