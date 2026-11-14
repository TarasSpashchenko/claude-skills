"""Report backticked paths in guide tables that do not resolve."""
import os
import re

PATH = re.compile(r"`([\w./-]+\.\w+)`")


def table_cells(lines):
    for number, line in enumerate(lines, 1):
        if line.startswith("|"):
            for cell in line.strip("|").split("|"):
                yield number, cell


def resolves(root, rel):
    """Match each path part against the folder listing, ignoring letter case."""
    current = root
    for part in rel.split("/"):
        names = {n.lower(): n for n in os.listdir(current)} if os.path.isdir(current) else {}
        if part.lower() not in names:
            return False
        current = os.path.join(current, names[part.lower()])
    return True


def check(root, guide):
    with open(os.path.join(root, guide)) as handle:
        lines = handle.read().splitlines()
    problems = []
    for number, cell in table_cells(lines):
        for rel in PATH.findall(cell):
            if not resolves(root, rel):
                problems.append(f"broken: {guide}:{number} {rel}")
    return problems
