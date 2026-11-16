"""Every third-party module imported by the server must be declared in requirements.txt.

Relying on a transitive dependency breaks the Docker image as soon as the package
that pulled it in stops depending on it.
"""
import ast
import re
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent.parent

# Import name -> distribution name, when they differ.
DISTRIBUTION_NAMES = {
    "dotenv": "python-dotenv",
    # starlette is the framework fastapi is built on and re-exports.
    "starlette": "fastapi",
}


def _imported_top_level_modules():
    modules = set()
    for path in SERVER_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules.add(node.module.split(".")[0])
    return modules


def _declared_distributions():
    declared = set()
    for line in (SERVER_DIR / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            declared.add(re.split(r"[<>=!~\[; ]", line, maxsplit=1)[0].lower())
    return declared


def test_third_party_imports_are_declared_in_requirements():
    # The code is importable both as top-level modules and as the `server` package.
    local_modules = {path.stem for path in SERVER_DIR.glob("*.py")} | {SERVER_DIR.name}
    third_party = _imported_top_level_modules() - set(sys.stdlib_module_names) - local_modules
    declared = _declared_distributions()

    missing = sorted(
        module
        for module in third_party
        if DISTRIBUTION_NAMES.get(module, module).lower().replace("_", "-") not in declared
    )

    assert missing == [], f"imported but not declared in requirements.txt: {missing}"
