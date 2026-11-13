#!/usr/bin/env python3
"""Review-kit helper for assessing AI-agent documentation. Standard library only.

Commands:
  setup   export the base docs and each candidate into a review root, with blind labels
  leaks   find words that would reveal a set's origin (model, branch, commit) in the root
  seal    make each set a standalone git repo, refusing while any leak is left
  facts   measure each set against base: sizes, section headings, caps, diffs
  routes  check the routing tables of an entry file (AGENTS.md): rows, gaps, duplicates
  paths   list backticked repository paths in the docs that do not resolve
  tally   count an agreed defect register on a board: kind x severity, origin, fix lists

Every command prints what it measured and the rule it applied, so its output can go into a
prompt as a "fact to verify" with the command that produced it.
"""
import argparse
import io
import os
import random
import re
import subprocess
import sys
import tarfile
from collections import Counter
from pathlib import Path

LABELS = "ABCDEFGH"
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "__pycache__"}


# --------------------------------------------------------------------------- shared helpers

def run_git(repo, *args, binary=False):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout if binary else result.stdout.decode().strip()


def extract_archive(repo, treeish, target, paths=()):
    """Extract `git archive <treeish> [paths]` into target (a tree-ish such as REV:subdir works)."""
    data = run_git(repo, "archive", "--format=tar", treeish, "--", *paths, binary=True)
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        if hasattr(tarfile, "data_filter"):
            archive.extractall(target, filter="data")
        else:
            archive.extractall(target)


def snapshot_repo(folder, message):
    """Make the export a standalone git repo, so reviewers can use git grep and see stray edits."""
    identity = ["-c", "user.name=review", "-c", "user.email=review@example.invalid"]
    for args in (["init", "-q", "-b", "review"], ["add", "-A"], [*identity, "commit", "-q", "-m", message]):
        run_git(folder, *args)


def text_lines(path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return None


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def set_folders(root):
    return sorted(p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"set-[A-Z]", p.name))


def is_inside(path, folder):
    path, folder = path.resolve(), folder.resolve()
    return path == folder or folder in path.parents


# --------------------------------------------------------------------------- setup

def parse_tool(spec):
    """NAME=REPO@REV[:SUBDIR] -> (name, repo, treeish)."""
    match = re.fullmatch(r"([\w.-]+)=(.+)@([^@:]+)(?::(.+))?", spec)
    if not match:
        sys.exit(f"--tool {spec!r}: expected NAME=REPO@REV[:SUBDIR]")
    name, repo, rev, subdir = match.groups()
    return name, Path(repo).expanduser(), f"{rev}:{subdir}" if subdir else rev


def existing_paths(repo, rev, paths):
    found = []
    for path in paths:
        probe = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{rev}:{path}"], capture_output=True)
        if probe.returncode == 0:
            found.append(path)
        else:
            print(f"note: {path} does not exist at base {rev}; base has no copy of it")
    return found


def cmd_setup(args):
    root, mapping = Path(args.root).expanduser(), Path(args.mapping).expanduser()
    if is_inside(mapping, root):
        sys.exit("refused: the mapping file must live outside the review root, where reviewers never read")
    if root.exists() and set_folders(root):
        sys.exit(f"refused: {root} already holds set folders; use a new root")
    repo = Path(args.repo).expanduser()
    candidates = list(args.candidate)
    if len(candidates) > len(LABELS):
        sys.exit(f"at most {len(LABELS)} candidates")
    if args.blind:
        random.SystemRandom().shuffle(candidates)

    lines = []
    for label, rev in zip(LABELS, candidates):
        sha = run_git(repo, "rev-parse", "--short", f"{rev}^{{commit}}")
        folder = root / f"set-{label}"
        extract_archive(repo, sha, folder)
        lines.append(f"{label}={rev} ({sha})")
        print(f"set-{label}: exported")

    base_sha = run_git(repo, "rev-parse", "--short", f"{args.base}^{{commit}}")
    extract_archive(repo, base_sha, root / "base", existing_paths(repo, base_sha, args.docs))
    print(f"base: docs exported ({', '.join(args.docs)})")

    for spec in args.tool or []:
        name, tool_repo, treeish = parse_tool(spec)
        extract_archive(tool_repo, treeish, root / name)
        print(f"{name}: exported from {treeish}")

    mapping.parent.mkdir(parents=True, exist_ok=True)
    blind_note = "blind (random order)" if args.blind else "not blind (order as given)"
    mapping.write_text(f"# label mapping, {blind_note}; base={args.base} ({base_sha})\n" + "\n".join(lines) + "\n")
    print(f"mapping written to {mapping} (outside the review root)")
    print("next: `leaks` with the model, tool and author names; neutralise every revealing hit; then `seal`")


# --------------------------------------------------------------------------- leaks

def mapping_terms(mapping):
    terms = []
    for line in Path(mapping).expanduser().read_text().splitlines():
        match = re.match(r"[A-Z]=(\S+) \((\w+)\)", line)
        if match:
            rev, sha = match.groups()
            terms += [rev, rev.rsplit("/", 1)[-1], sha]
    return terms


def same_in_every_set(root, rel_in_set):
    """True when the file exists with identical bytes in every set: then it cannot tell sets apart."""
    copies = [folder / rel_in_set for folder in set_folders(root)]
    if len(copies) < 2 or not all(c.is_file() for c in copies):
        return False
    first = copies[0].read_bytes()
    return all(c.read_bytes() == first for c in copies[1:])


def leak_pattern(args):
    terms = sorted({t for t in (args.term or []) + (mapping_terms(args.mapping) if args.mapping else []) if t})
    if not terms:
        sys.exit("give --term words (model names, branch names, authors) and/or --mapping")
    return re.compile("|".join(re.escape(t) for t in terms), re.IGNORECASE), len(terms)


def scan_files(root, pattern):
    """Print revealing hits in paths and text; return (count, files that are identical in every set)."""
    revealing, shared_files = 0, set()
    for path in walk_files(root):
        rel = path.relative_to(root)
        path_hit = bool(pattern.search(str(rel)))
        hits = [(n, line) for n, line in enumerate(text_lines(path) or [], 1) if pattern.search(line)]
        if not (path_hit or hits):
            continue
        in_set = rel.parts[0].startswith("set-")
        if in_set and same_in_every_set(root, Path(*rel.parts[1:])):
            shared_files.add(Path(*rel.parts[1:]))
            continue
        if path_hit:
            print(f"{rel}: (in the path)")
            revealing += 1
        for number, line in hits:
            print(f"{rel}:{number}: {line.strip()[:160]}")
            revealing += 1
    return revealing, shared_files


def scan_history(root, pattern):
    """Print hits in the git history of sealed sets that are not the same in every set; return the count.

    walk_files skips .git, where objects are compressed, so a word removed after a commit is only
    visible here."""
    per_set = {}
    for folder in set_folders(root):
        if not (folder / ".git").exists():
            continue
        log = run_git(folder, "log", "-p", "--all", "--format=%s")
        per_set[folder.name] = {line.lstrip("+- ").strip() for line in log.splitlines() if pattern.search(line)}
    if not per_set:
        return 0
    shared = set.intersection(*per_set.values()) if len(per_set) > 1 else set()
    revealing = 0
    for name, lines in per_set.items():
        for line in sorted(lines - shared):
            print(f"{name} (git history): {line[:160]}")
            revealing += 1
    return revealing


def cmd_leaks(args):
    root = Path(args.root).expanduser()
    pattern, count = leak_pattern(args)
    revealing, shared_files = scan_files(root, pattern)
    revealing += scan_history(root, pattern)
    print(f"searched for {count} term(s), case-insensitive, in every text file, path and set history under {root}")
    print(f"{revealing} hit(s) that differ between sets or sit outside them (review each one); "
          f"{len(shared_files)} file(s) with hits are identical in every set, so they reveal nothing")
    return 1 if revealing else 0


def cmd_seal(args):
    """Make each set a standalone git repo, only once no revealing hit is left."""
    root = Path(args.root).expanduser()
    pattern, _ = leak_pattern(args)
    revealing = scan_files(root, pattern)[0] + scan_history(root, pattern)
    if revealing:
        sys.exit(f"refused: {revealing} revealing hit(s) above; neutralise them in every set, then seal")
    for folder in set_folders(root):
        if (folder / ".git").exists():
            sys.exit(f"refused: {folder.name} is already a git repo; its history may hold what you removed. "
                     "Delete its .git folder, check again, then seal")
    for folder in set_folders(root):
        snapshot_repo(folder, f"{folder.name} snapshot")
        print(f"{folder.name}: sealed (git repo, branch review, one commit)")
    return 0


# --------------------------------------------------------------------------- facts

def heading_count(guides, heading, exact):
    target = f"## {heading}"
    count = 0
    for path in guides:
        for line in text_lines(path) or []:
            if (line.rstrip() == target) if exact else (line.rstrip().casefold() == target.casefold()):
                count += 1
                break
    return count


def measure(folder, args):
    docs_dir, entry, guides_dir = folder / args.docs_dir, folder / args.entry, folder / args.guides
    guides = sorted(guides_dir.rglob("*.md")) if guides_dir.is_dir() else []
    entry_lines = text_lines(entry) or []
    over_cap = [f"{p.relative_to(guides_dir)} ({n})" for p in guides
                if (n := len(text_lines(p) or [])) > args.cap]
    return {
        "docs_bytes": sum(p.stat().st_size for p in walk_files(docs_dir)) if docs_dir.is_dir() else 0,
        "entry_bytes": entry.stat().st_size if entry.is_file() else 0,
        "entry_lines": len(entry_lines),
        "guides": len(guides),
        "headings": {h: (heading_count(guides, h, False), heading_count(guides, h, True)) for h in args.heading},
        "over_cap": over_cap,
        "entry_over_cap": len(entry_lines) > args.entry_cap,
    }


def with_change(value, base_value):
    if not base_value or value == base_value:
        return f"{value:,}"
    return f"{value:,} ({(value - base_value) / base_value:+.1%})"


def write_diffs(root, folder, args):
    facts = root / "facts"
    facts.mkdir(exist_ok=True)
    label = folder.name.removeprefix("set-")
    pairs = {f"diff-base-{label}-docs.patch": args.docs_dir, f"diff-base-{label}-entry.patch": args.entry}
    for name, rel in pairs.items():
        result = subprocess.run(["diff", "-ruN", str(root / "base" / rel), str(folder / rel)], capture_output=True)
        (facts / name).write_bytes(result.stdout)


def cmd_facts(args):
    root = Path(args.root).expanduser()
    folders = [root / "base", *set_folders(root)]
    data = {f.name: measure(f, args) for f in folders}
    base = data["base"]
    rows = [
        ("`" + args.docs_dir + "` bytes", lambda d: with_change(d["docs_bytes"], base["docs_bytes"])),
        ("`" + args.entry + "` bytes", lambda d: with_change(d["entry_bytes"], base["entry_bytes"])),
        ("`" + args.entry + "` lines", lambda d: with_change(d["entry_lines"], base["entry_lines"])),
        ("guides (`*.md`)", lambda d: str(d["guides"])),
    ]
    for h in args.heading:
        rows.append((f"guides with `## {h}`", lambda d, h=h: f"{d['headings'][h][0]}"
                     + ("" if d["headings"][h][0] == d["headings"][h][1] else f" (exact case {d['headings'][h][1]})")))
    rows.append((f"guides over {args.cap} lines", lambda d: ", ".join(d["over_cap"]) or "none"))
    rows.append((f"`{args.entry}` over {args.entry_cap} lines", lambda d: "yes" if d["entry_over_cap"] else "no"))
    out = ["| Measure | " + " | ".join(data) + " |", "|---|" + "---|" * len(data)]
    out += [f"| {name} | " + " | ".join(fn(d) for d in data.values()) + " |" for name, fn in rows]
    out.append("")
    out.append(f"Rule: bytes of every file under `{args.docs_dir}`; a heading counts once per guide, matched "
               "as a whole line, case-insensitive (exact-case count shown where it differs).")
    for folder in folders[1:]:
        write_diffs(root, folder, args)
    table = "\n".join(out)
    (root / "facts").mkdir(exist_ok=True)
    (root / "facts" / "sizes.md").write_text(table + "\n")
    print(table)
    print(f"\nwritten: {root}/facts/sizes.md and diff-base-<label>-*.patch")


# --------------------------------------------------------------------------- routes

def markdown_tables(lines):
    """Yield (section heading, header cells, [(line number, cells)]) for each table."""
    section, index = "", 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?\s*$", lines[index + 1]):
            header = split_row(line)
            rows, index = [], index + 2
            while index < len(lines) and lines[index].startswith("|"):
                rows.append((index + 1, split_row(lines[index])))
                index += 1
            yield section, header, rows
            continue
        index += 1


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def cmd_routes(args):
    folder = Path(args.set).expanduser()
    entry_lines = text_lines(folder / args.entry) or []
    guides_dir = folder / args.guides
    guides = sorted(str(p.relative_to(folder)) for p in guides_dir.rglob("*.md"))
    path_re = re.compile(re.escape(args.guides.rstrip("/")) + r"/[\w./-]+?\.md")
    named_anywhere, named_in_routes = set(), set()
    for section, header, rows in markdown_tables(entry_lines):
        named = [(n, p) for n, cells in rows for p in path_re.findall(" | ".join(cells))]
        paths = [p for _, p in named]
        named_anywhere.update(paths)
        is_route = any(re.fullmatch(args.route_col, h, re.IGNORECASE) for h in header)
        if is_route:
            named_in_routes.update(paths)
        print(f"## {section or '(no heading)'}: {len(rows)} rows, {len(set(paths))} distinct guide paths"
              + (" [routing table]" if is_route else ""))
        repeated = sorted({p for p in paths if paths.count(p) > 1})
        if repeated and not is_route:
            print(f"  guide named in more than one row: {repeated}")
        example_cols = [i for i, h in enumerate(header) if re.search(r"example|request|intent", h, re.IGNORECASE)]
        phrases = {}
        for n, cells in rows:
            for i in example_cols:
                if i < len(cells):
                    for phrase in re.split(r"[;,]", cells[i]):
                        phrase = phrase.strip().strip("\"'`").lower()
                        if phrase:
                            phrases.setdefault(phrase, set()).add(n)
        shared = {k: sorted(v) for k, v in phrases.items() if len(v) > 1}
        if shared:
            print(f"  phrase in more than one row (line numbers): {shared}")
        bare = sorted({n for n, cells in rows for p in path_re.findall(" | ".join(cells)) if f"`{p}`" not in " | ".join(cells)})
        if bare:
            print(f"  rows with a guide path outside backticks (lines): {bare}")
    print(f"guides named in no table: {[g for g in guides if g not in named_anywhere] or 'none'}")
    print(f"guides named in no routing table (header matches {args.route_col!r}): "
          f"{[g for g in guides if g not in named_in_routes] or 'none'}")
    missing = sorted({p for line in entry_lines for p in path_re.findall(line) if not (folder / p).exists()})
    print(f"named guide paths that do not exist: {missing or 'none'}")
    print(f"rule: tables found in {args.entry}; guide paths match {path_re.pattern}; {len(guides)} guides on disk")


# --------------------------------------------------------------------------- paths

def case_mismatch(folder, rel):
    """Return the real spelling when rel exists only with different letter case."""
    current = folder
    for part in Path(rel).parts:
        if not current.is_dir():
            return None
        names = {p.name.lower(): p.name for p in current.iterdir()}
        real = names.get(part.lower())
        if real is None:
            return None
        current = current / real
    return str(current.relative_to(folder))


def cmd_paths(args):
    folder = Path(args.set).expanduser()
    files = [folder / args.entry, *sorted((folder / args.guides).rglob("*.md"))]
    token = re.compile(r"`([\w@.-]+(?:/[\w@.\[\]-]+)+\.\w+)(?::[\d,-]+)?(?:::\w+)?`")
    prefixes = tuple(args.prefix)
    problems = 0
    for path in files:
        for number, line in enumerate(text_lines(path) or [], 1):
            for rel in token.findall(line):
                if prefixes and not rel.startswith(prefixes):
                    continue
                if (folder / rel).exists():
                    continue
                real = case_mismatch(folder, rel)
                note = f"exists only as {real} (letter case)" if real else "does not exist"
                print(f"{path.relative_to(folder)}:{number}: `{rel}` {note}")
                problems += 1
    print(f"rule: backticked tokens with a slash and a file extension"
          + (f", starting with {', '.join(prefixes)}" if prefixes else "")
          + f", resolved against {folder}; {problems} unresolved")
    return 1 if problems else 0


# --------------------------------------------------------------------------- tally

ORIGINS = {"inh": "inherited", "inherited": "inherited", "run": "run", "run-c": "run-c",
           "run-contradiction": "run-c"}


def register_rows(board_text):
    """Find the table whose header has Kind and Severity columns; return (header, rows)."""
    for _, header, rows in markdown_tables(board_text.splitlines()):
        lower = [h.lower() for h in header]
        if "kind" in lower and "severity" in lower:
            return lower, [cells for _, cells in rows]
    sys.exit("no table with Kind and Severity columns on the board")


def cmd_tally(args):
    header, rows = register_rows(Path(args.board).expanduser().read_text())
    col = {name: header.index(name) for name in ("id", "kind", "severity", "origin", "status") if name in header}
    if "origin" not in col or "id" not in col:
        sys.exit("the register needs ID, Kind, Severity and Origin columns")
    agreed, set_aside, problems = [], [], []
    for cells in rows:
        cells = cells + [""] * (len(header) - len(cells))
        row_id = cells[col["id"]].strip("* ")
        status = cells[col["status"]] if "status" in col else "agreed"
        kind, severity = cells[col["kind"]].lower(), cells[col["severity"]].lower()
        origin = ORIGINS.get(cells[col["origin"]].lower())
        if kind not in {"false", "contradiction", "broken", "structure"} or severity not in {"major", "minor"} or not origin:
            problems.append(f"{row_id}: kind={kind!r} severity={severity!r} origin={cells[col['origin']]!r}")
            continue
        (agreed if status.lower().startswith("agreed") else set_aside).append((row_id, kind, severity, origin, status))

    by_kind = Counter((k, s) for _, k, s, _, _ in agreed)
    print(f"agreed rows: {len(agreed)} ({sum(1 for r in agreed if r[2] == 'major')} major, "
          f"{sum(1 for r in agreed if r[2] == 'minor')} minor)")
    for kind in ("false", "contradiction", "broken", "structure"):
        print(f"  {kind}: {by_kind[(kind, 'major')]} major / {by_kind[(kind, 'minor')]} minor")
    origins = Counter(r[3] for r in agreed)
    print(f"origin: inherited {origins['inherited']}, run {origins['run']}, run-c {origins['run-c']} "
          f"-> run-made under rule a: {origins['run']}, under rule b: {origins['run'] + origins['run-c']}")
    majors = [r[0] for r in agreed if r[2] == "major"]
    run_minors = [r[0] for r in agreed if r[2] == "minor" and r[3] in {"run", "run-c"}]
    later = [r[0] for r in agreed if r[2] == "minor" and r[3] == "inherited"]
    print(f"fix before merge (every major + every run-made minor, rule b): {len(majors) + len(run_minors)}")
    print(f"  majors ({len(majors)}): {', '.join(majors) or 'none'}")
    print(f"  run-made minors ({len(run_minors)}): {', '.join(run_minors) or 'none'}")
    print(f"can wait (inherited minors, {len(later)}): {', '.join(later) or 'none'}")
    if set_aside:
        print(f"not agreed, counted apart ({len(set_aside)}): " + ", ".join(f"{r[0]} [{r[4]}]" for r in set_aside))
    if problems:
        print("rows with values outside the method (fix them before quoting any count):")
        for line in problems:
            print(f"  {line}")
        return 1
    return 0


# --------------------------------------------------------------------------- CLI

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("setup", help="export base docs and candidates into a review root")
    p.add_argument("--repo", required=True, help="git repository holding the candidates")
    p.add_argument("--root", required=True, help="new review root, outside the repository")
    p.add_argument("--base", required=True, help="revision the runs started from (usually the merge-base)")
    p.add_argument("--candidate", action="append", required=True, help="branch or commit; repeat per candidate")
    p.add_argument("--docs", nargs="+", default=["AGENTS.md", "CLAUDE.md", ".ai-run"], help="doc paths exported from base")
    p.add_argument("--mapping", required=True, help="private file for the label mapping, outside the root")
    p.add_argument("--tool", action="append", help="NAME=REPO@REV[:SUBDIR], e.g. the generator or the consumers")
    p.add_argument("--no-blind", dest="blind", action="store_false", help="keep the given order (one candidate)")
    p.set_defaults(func=cmd_setup)

    for name, func, helptext in (("leaks", cmd_leaks, "find words that reveal a set's origin"),
                                 ("seal", cmd_seal, "make each set a git repo once no leak is left")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--root", required=True)
        p.add_argument("--term", action="append", help="word to find, case-insensitive; repeat")
        p.add_argument("--mapping", help="also search the branch names and commit ids in this mapping file")
        p.set_defaults(func=func)

    for name, func, helptext in (("facts", cmd_facts, "measure each set against base"),
                                 ("routes", cmd_routes, "check the entry file's routing tables"),
                                 ("paths", cmd_paths, "list backticked paths that do not resolve")):
        p = sub.add_parser(name, help=helptext)
        if name == "facts":
            p.add_argument("--root", required=True)
            p.add_argument("--docs-dir", default=".ai-run", help="folder of generated docs, for byte counts and diffs")
            p.add_argument("--heading", action="append", default=None, help="section heading to count; repeat")
            p.add_argument("--cap", type=int, default=400, help="line cap per guide")
            p.add_argument("--entry-cap", type=int, default=300, help="line cap for the entry file")
        else:
            p.add_argument("--set", required=True, help="one set folder (or any checkout)")
        p.add_argument("--entry", default="AGENTS.md")
        p.add_argument("--guides", default=".ai-run/guides")
        if name == "routes":
            p.add_argument("--route-col", default=r"P0( guide)?", help="regex for the header that marks a routing table")
        if name == "paths":
            p.add_argument("--prefix", action="append", default=[], help="only check tokens starting with this; repeat")
        p.set_defaults(func=func)

    p = sub.add_parser("tally", help="count the defect register on a board")
    p.add_argument("--board", required=True)
    p.set_defaults(func=cmd_tally)

    args = parser.parse_args()
    if args.command == "facts" and not args.heading:
        args.heading = ["Overview", "Examples", "Common pitfalls", "Quick reference"]
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
