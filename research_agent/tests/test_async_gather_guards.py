"""Waechter gegen falsch aufgebaute ``asyncio.gather``-Aufrufe.

Hintergrund: In Run 2 (05.11.2026) brach Phase 7b siebenmal mit
``TypeError: An asyncio.Future, a coroutine or an awaitable is required``
ab, weil ``asyncio.gather(_analyze_one(h) for h in ...)`` einen Generator
statt entpackter Coroutines bekam. Der Fehler kostete jeden dritten Zyklus
und blieb im Lauf unbemerkt (der Zyklus wurde verworfen, der Lauf lief weiter).

Der Test ist statisch: er liest den Code per ``ast`` und meldet jeden
``gather``-Aufruf, der ein Generator-Objekt uebergeben bekommt, ohne es mit
``*`` zu entpacken. Damit wird die Fehlerklasse an allen Modulen geprueft,
nicht nur an der damals betroffenen Stelle.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


def _bad_gather_calls(tree: ast.AST) -> list[ast.Call]:
    """Return gather() calls that receive a generator without unpacking."""
    bad: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "gather"):
            continue
        if any(isinstance(arg, ast.Starred) for arg in node.args):
            continue
        if len(node.args) == 1 and isinstance(
            node.args[0], (ast.GeneratorExp, ast.ListComp)
        ):
            # gather(genexp) is always wrong; gather([a(), b()]) is a plain
            # list and therefore also not awaitable.
            bad.append(node)
    return bad


class GatherCallShapeTest(unittest.TestCase):
    def test_no_gather_call_unpacks_nothing(self):
        offenders: list[str] = []
        for path in sorted(PACKAGE.rglob("*.py")):
            if "tests" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError:
                continue
            for node in _bad_gather_calls(tree):
                offenders.append(f"{path.relative_to(PACKAGE)}:{node.lineno}")
        self.assertEqual(
            offenders,
            [],
            "asyncio.gather braucht entpackte Coroutines (z.B. *[...]): "
            + ", ".join(offenders),
        )

    def test_detector_flags_the_run2_pattern(self):
        # Der Test darf nicht stillschweigend gruen sein, wenn der Detektor
        # kaputt ist: der historische Fehler muss erkannt werden.
        broken = ast.parse(
            "async def f():\n"
            "    await asyncio.gather(_analyze_one(h) for h in hyps[:2])\n"
        )
        self.assertEqual(len(_bad_gather_calls(broken)), 1)

        fixed = ast.parse(
            "async def f():\n"
            "    await asyncio.gather(*[_analyze_one(h) for h in hyps[:2]])\n"
        )
        self.assertEqual(_bad_gather_calls(fixed), [])

        with_results = ast.parse(
            "async def f():\n"
            "    await asyncio.gather(*tasks, return_exceptions=True)\n"
        )
        self.assertEqual(_bad_gather_calls(with_results), [])


if __name__ == "__main__":
    unittest.main()
