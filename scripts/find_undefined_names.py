#!/usr/bin/env python3
"""Find names a function reads but never binds anywhere.

Why this exists: a single `if all_facts:` in `orchestrator._run_cycle` read a
variable that only exists inside another method. Python compiles that happily,
the test suite never runs that line offline, and the NameError only shows up at
runtime - where it killed every cycle after the analysis phase for a whole run.

The check is a small static pass over the AST: for each function, collect the
names it binds (assignments, arguments, imports, for/with targets, nested defs),
the names declared `global`/`nonlocal`, the bindings of enclosing functions
(closures) and the module level; every loaded name outside that set is reported.

    python scripts/find_undefined_names.py [pfad ...]

Known limits: attribute names are not checked, a name bound anywhere in a
function counts as bound (so a genuine use-before-assignment inside one function
is not reported), and dynamic lookups (globals(), locals()) are invisible.
"""

import ast
import builtins
import sys
from pathlib import Path

BUILTINS = set(dir(builtins)) | {
    "__file__", "__name__", "__doc__", "__package__", "__spec__", "__loader__",
    "__builtins__", "__debug__",
}


class Scope(ast.NodeVisitor):
    """Names bound directly in this scope, without descending into nested ones."""

    def __init__(self):
        self.bound = set()
        self.declared = set()
        self.loads = []

    def visit_FunctionDef(self, node):
        self.bound.add(node.name)
        self._arguments(node.args)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.bound.add(node.name)

    def visit_Lambda(self, node):
        self._arguments(node.args)

    def _arguments(self, args):
        for arg in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
            self.bound.add(arg.arg)
        if args.vararg:
            self.bound.add(args.vararg.arg)
        if args.kwarg:
            self.bound.add(args.kwarg.arg)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.bound.add(node.id)
        else:
            self.loads.append(node)

    def visit_Global(self, node):
        self.declared.update(node.names)

    def visit_Nonlocal(self, node):
        self.declared.update(node.names)

    def visit_Import(self, node):
        for alias in node.names:
            self.bound.add((alias.asname or alias.name).split(".")[0])

    visit_ImportFrom = visit_Import

    def visit_ExceptHandler(self, node):
        if node.name:
            self.bound.add(node.name)
        self.generic_visit(node)


def module_bindings(tree) -> set:
    """Everything the module level binds, plus builtins."""
    names = set(BUILTINS)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            # Only module-level stores matter; a function-local store is not a
            # module binding, so walk top-level statements instead of the whole tree.
            pass
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        names.add(sub.id)
    return names


def scan(tree, label: str, module_names: set) -> list:
    findings = []

    def visit_function(node, chain: set):
        s = Scope()
        s._arguments(node.args)      # the function's own parameters
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                s.bound.add(statement.name)
            else:
                s.visit(statement)
        known = BUILTINS | module_names | chain | s.bound | s.declared
        for load in s.loads:
            if load.id not in known:
                findings.append((label, node.name, load.id, load.lineno))
        inner = chain | s.bound
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit_function(statement, inner)
            elif isinstance(statement, ast.ClassDef):
                for method in statement.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # A class body is not a closure over its methods.
                        visit_function(method, chain)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visit_function(node, set())
    return findings


def check(paths) -> list:
    findings = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        findings += scan(tree, str(path), module_bindings(tree))
    return findings


def _self_test() -> None:
    demo = (
        "def outer():\n"
        "    bound_here = []\n"
        "    def inner():\n"
        "        only_inner = []\n"
        "        return only_inner\n"
        "    if only_inner:\n"
        "        return bound_here\n"
    )
    found = check([_write_demo(demo)])
    assert [f[2] for f in found] == ["only_inner"], found
    print("Selbsttest ok: der Scanner findet den Fehler, der einen ganzen Lauf killte")


def _write_demo(source: str) -> Path:
    import tempfile
    path = Path(tempfile.mkdtemp()) / "demo.py"
    path.write_text(source, encoding="utf-8")
    return path


def main(argv) -> int:
    _self_test()
    targets = [Path(p) for p in argv[1:]] or sorted(Path("research_agent").rglob("*.py"))
    files = [
        p for p in targets
        if p.suffix == ".py" and "__pycache__" not in str(p)
    ]
    findings = check(files)
    print(f"Geprüfte Dateien: {len(files)}")
    if not findings:
        print("Keine undefinierten Namen gefunden.")
        return 0
    print(f"Undefinierte Namen: {len(findings)}")
    for path, function, name, line in findings:
        print(f"  {path}:{line}  '{name}' in {function}()")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
