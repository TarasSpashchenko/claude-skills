#!/usr/bin/env python3
"""Discussion-board helper. Standard library only.

Commands:
  status   show whose turn it is (in group mode, also who has submitted)
  publish  publish a full new board atomically, ending with one marker line
  wait     block until the board ends with a given marker (or, in group mode, any later
           round), or with DISCUSSION-CLOSED
  submit   group mode: store one participant's submission for the open round, exactly once
  collect  group mode: wait until every rostered participant has submitted, or the deadline
  edits    check, apply or verify an edit register (see references/edit-outcomes.md)

The board ends with one marker line, `END-OF-TURN <N> NEXT=<TAG>`, or `DISCUSSION-CLOSED`.
`publish` refuses to write when the board's last line is not the expected marker, which
catches a concurrent edit by the other side. Every write goes through a temporary file in
the target's own folder and a rename, so a reader never sees half a file.

Group mode (references/group-mode.md): Claude alone publishes the board, and
`END-OF-TURN <R> NEXT=ALL` opens round R. The board's `Roster:` and `Round:` lines name the
participants and the round's deadline. Each participant stores its round-R text with
`submit`, as `rounds/<R>/<TAG>.md`, which is created once and never overwritten.
"""
import argparse
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MARKER = re.compile(r"^(END-OF-TURN (\d+) NEXT=([A-Z][A-Z0-9_-]*)|DISCUSSION-CLOSED)$")
CLOSED = "DISCUSSION-CLOSED"
EXIT_PROBLEMS, EXIT_STALE, EXIT_BAD_DRAFT, EXIT_DEADLINE, EXIT_TIMEOUT = 1, 2, 3, 4, 124

ALL = "ALL"  # reserved tag: a marker with NEXT=ALL opens a group round for every participant
COORDINATOR = "CLAUDE"
MAX_PARTICIPANTS = 5  # the user's cap, Claude included
NOT_STARTED = "not-started"
TAG = re.compile(r"^[A-Z][A-Z0-9_-]*$")
ROSTER_LINE = re.compile(r"^Roster:[ \t]*(.*)$", re.MULTILINE)
ROUND_LINE = re.compile(
    r"^Round:[ \t]*(\d+)[ \t]+(discussion|confirmation)[ \t]*,[ \t]*deadline[ \t]+(\S+)[ \t]*$", re.MULTILINE
)


def default_file_mode():
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


def write_atomically(path, text):
    """Write through a temporary file in the same folder.

    mkstemp creates the file private (0600); an existing file keeps its permissions and a new
    one gets the usual umask-based mode, so a counterpart running as another user can read it.
    """
    mode = path.stat().st_mode & 0o777 if path.exists() else default_file_mode()
    handle, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(handle, "w") as out:
        out.write(text)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def last_line(text):
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-1].strip() if lines else ""


def ending_marker(board):
    if not board.exists():
        return ""
    last = last_line(board.read_text())
    return last if MARKER.match(last) else ""


# --- status, publish, wait -------------------------------------------------------------


def status(board):
    last = ending_marker(board)
    match = MARKER.match(last)
    if not match:
        print("no marker: the opening turn has not been published")
    elif last == CLOSED:
        print(f"closed: {CLOSED}")
    else:
        print(f"turn {match.group(2)} published; next: {match.group(3)} (marker: {last})")
        if match.group(3) == ALL:
            print_round_state(board, int(match.group(2)))


def strip_trailing_markers(lines):
    while lines and (not lines[-1].strip() or MARKER.match(lines[-1].strip())):
        lines.pop()
    return lines


def publish(board, draft, expect_last, marker):
    if not MARKER.match(marker):
        sys.exit(f"invalid marker: {marker!r}")
    current = ending_marker(board)
    if expect_last == "none":
        if current:
            print(f"refused: the board already ends with a marker ({current})", file=sys.stderr)
            sys.exit(EXIT_STALE)
    elif current != expect_last:
        print(f"refused: expected last line {expect_last!r}, found {current!r}", file=sys.stderr)
        sys.exit(EXIT_STALE)
    lines = strip_trailing_markers(draft.read_text().splitlines())
    stray = [line for line in lines if MARKER.match(line.strip())]
    if stray:
        print(f"refused: the draft has marker lines in its body: {stray}", file=sys.stderr)
        sys.exit(EXIT_BAD_DRAFT)
    body = "\n".join(lines)
    opened_round = group_round(marker)
    if opened_round is not None:
        check_group_header(body, opened_round)
    write_atomically(board, body + "\n\n" + marker + "\n")
    print(f"published {board} ending with: {marker}")


def exact_marker(marker):
    if not MARKER.match(marker):
        sys.exit(f"invalid marker: {marker!r}")
    return lambda found: found in (marker, CLOSED)


def round_after(round_number):
    """Group mode: ready on any round later than `round_number`, so a participant that missed
    a round resynchronizes instead of waiting for a marker that has already gone by."""
    def ready(found):
        later = group_round(found)
        return found == CLOSED or (later is not None and later > round_number)
    return ready


def wait(board, is_ready, timeout, interval, settle):
    """Return 0 once the board's marker satisfies `is_ready`, 124 on timeout."""
    deadline = time.monotonic() + timeout
    while True:
        found = ending_marker(board)
        if is_ready(found):
            time.sleep(settle)  # lets a writer that does not rename atomically finish
            print(f"ready: {found}")
            return 0
        if time.monotonic() >= deadline:
            print(f"timeout: the board still ends with {found or 'no marker'}")
            return EXIT_TIMEOUT
        time.sleep(interval)


# --- group mode: roster, rounds, submissions ---------------------------------------------


@dataclass
class GroupHeader:
    roster: list
    round: int
    purpose: str
    deadline: datetime = None  # None until the user says go for round 1


def refuse(message, code):
    print(f"refused: {message}", file=sys.stderr)
    sys.exit(code)


def group_round(marker):
    """The round that `marker` opens for everyone, or None for any other marker."""
    match = MARKER.match(marker)
    if match and match.group(3) == ALL:
        return int(match.group(2))
    return None


def roster_problem(roster):
    invalid = [tag for tag in roster if not TAG.match(tag)]
    if invalid:
        return f"invalid tags {invalid}"
    if len(set(roster)) != len(roster):
        return "a tag appears twice in the roster"
    if ALL in roster:
        return f"{ALL} is reserved and cannot be a participant"
    if COORDINATOR not in roster:
        return f"the roster must include {COORDINATOR}, a full participant"
    if len(roster) > MAX_PARTICIPANTS:
        return f"{len(roster)} participants exceed the cap of {MAX_PARTICIPANTS}, {COORDINATOR} included"
    return ""


def parse_deadline(value):
    if value == NOT_STARTED:
        return None
    deadline = datetime.fromisoformat(value)
    if deadline.tzinfo is None:
        raise ValueError(f"deadline {value!r} needs a UTC offset, for example 2026-10-27T11:40+02:00")
    return deadline


def parse_header(text):
    """Read the board's `Roster:` and `Round:` lines; raise ValueError naming the problem."""
    roster_line, round_line = ROSTER_LINE.search(text), ROUND_LINE.search(text)
    if not roster_line:
        raise ValueError("no 'Roster:' line")
    if not round_line:
        raise ValueError(f"no 'Round: <R> <discussion|confirmation>, deadline <ISO time|{NOT_STARTED}>' line")
    roster = roster_line.group(1).replace(",", " ").split()
    problem = roster_problem(roster)
    if problem:
        raise ValueError(problem)
    number, purpose, deadline = round_line.groups()
    return GroupHeader(roster, int(number), purpose, parse_deadline(deadline))


def check_group_header(text, round_number):
    try:
        header = parse_header(text)
    except ValueError as error:
        refuse(f"group board header: {error}", EXIT_BAD_DRAFT)
    if header.round != round_number:
        refuse(f"the 'Round:' line says {header.round}, the marker opens round {round_number}", EXIT_BAD_DRAFT)


def open_round_header(board, round_number):
    """The header of `board`, provided it is the open board of round `round_number`."""
    current = ending_marker(board)
    if group_round(current) != round_number:
        refuse(f"round {round_number} is not open; the board ends with {current or 'no marker'!r}", EXIT_STALE)
    try:
        header = parse_header(board.read_text())
    except ValueError as error:
        refuse(f"group board header: {error}", EXIT_STALE)
    if header.round != round_number:
        refuse(f"the 'Round:' line says {header.round}, the marker says {round_number}", EXIT_STALE)
    return header


def deadline_passed(header):
    return header.deadline is not None and datetime.now(timezone.utc) >= header.deadline


def submission_path(board, round_number, tag):
    return board.parent / "rounds" / str(round_number) / f"{tag}.md"


def round_state(board, header):
    received = [tag for tag in header.roster if submission_path(board, header.round, tag).exists()]
    missing = [tag for tag in header.roster if tag not in received]
    return received, missing


def describe_round(board, header):
    received, missing = round_state(board, header)
    deadline = header.deadline.isoformat() if header.deadline else NOT_STARTED
    return (f"round {header.round} ({header.purpose}), deadline {deadline}: "
            f"received {', '.join(received) or 'none'}; missing {', '.join(missing) or 'none'}")


def print_round_state(board, round_number):
    try:
        header = parse_header(board.read_text())
    except ValueError as error:
        print(f"group board header problem: {error}")
        return
    if header.round != round_number:
        print(f"group board header problem: the 'Round:' line says {header.round}, the marker {round_number}")
        return
    print(describe_round(board, header))


def create_exclusively(path, text):
    """Publish `text` at `path` only if `path` does not exist yet; return False if it does.

    A complete temporary file is hard-linked to the target: the link fails when the target
    exists, so a reader never sees half a file and nothing is ever overwritten.
    """
    handle, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w") as out:
            out.write(text)
        os.chmod(tmp, default_file_mode())
        os.link(tmp, path)
        return True
    except FileExistsError:
        return False
    except OSError as error:
        refuse(f"this file system cannot create files exclusively ({error}); nothing was written", EXIT_PROBLEMS)
    finally:
        os.unlink(tmp)


def submit(board, round_number, tag, draft):
    header = open_round_header(board, round_number)
    if tag not in header.roster:
        refuse(f"{tag} is not in the roster {' '.join(header.roster)}", EXIT_STALE)
    if deadline_passed(header):
        refuse(f"the round {round_number} deadline passed at {header.deadline.isoformat()}", EXIT_STALE)
    text = draft.read_text()
    stray = [line for line in text.splitlines() if MARKER.match(line.strip())]
    if stray:
        refuse(f"the submission has marker lines in it: {stray}", EXIT_BAD_DRAFT)
    target = submission_path(board, round_number, tag)
    target.parent.mkdir(parents=True, exist_ok=True)
    if create_exclusively(target, text):
        print(f"submitted {target}")
    elif target.read_text() == text:
        print(f"already submitted, identical: {target}")
    else:
        refuse(f"{target} already holds a different submission; submissions are never overwritten", EXIT_STALE)


def collect(board, round_number, timeout, interval):
    """Return 0 when every rostered participant has submitted, 4 once the round's deadline
    has passed with some missing, 124 when this call's own timeout ends first.

    The timeout bounds this call only: the deadline is the one published on the board, so
    repeating the call, or resuming after a crash, never extends it.
    """
    header = open_round_header(board, round_number)
    stop = time.monotonic() + timeout
    while True:
        _, missing = round_state(board, header)
        if not missing:
            label, code = "complete", 0
        elif deadline_passed(header):
            label, code = "deadline passed", EXIT_DEADLINE
        elif time.monotonic() >= stop:
            label, code = "timeout, the round is still open", EXIT_TIMEOUT
        else:
            time.sleep(interval)
            continue
        print(f"{label}: {describe_round(board, header)}")
        return code


# --- edit register ---------------------------------------------------------------------

EDIT_HEADING = re.compile(r"^(#{2,6})\s+(E-\d+)\b.*?\b(proposed|countered|agreed|dropped)\s*$")
ANY_HEADING = re.compile(r"^(#{1,6})\s")
FENCE_OPEN = re.compile(r"^(~{3,})(current|after|new)\s*$")
FILE_LINE = re.compile(r"^File:\s*`?([^`]+?)`?\s*$")
TRACE_LINE = re.compile(r"^Traces to:\s*\S")


@dataclass
class Edit:
    edit_id: str
    status: str
    level: int
    file: str = ""
    traced: bool = False
    blocks: dict = field(default_factory=dict)

    @property
    def anchor(self):
        return self.blocks.get("current", self.blocks.get("after", ""))

    @property
    def operation(self):
        if "after" in self.blocks:
            return "insert"
        return "replace" if self.blocks.get("new") else "delete"

    def word_delta(self):
        removed = 0 if self.operation == "insert" else len(self.anchor.split())
        return len(self.blocks.get("new", "").split()) - removed

    def shape_problem(self):
        if not self.file:
            return "no 'File:' line"
        if ("current" in self.blocks) == ("after" in self.blocks):
            return "needs exactly one ~~~current or ~~~after block"
        if not self.anchor.strip():
            return "empty anchor"
        if self.operation == "insert" and not self.blocks.get("new", "").strip():
            return "an insert needs a non-empty ~~~new block"
        return ""


class RegisterParser:
    """Reads `E-xx` entries: heading with a status, File:, Traces to:, and fenced blocks."""

    def __init__(self):
        self.edits, self.edit, self.fence, self.kind, self.fenced = [], None, "", "", []

    def parse(self, text):
        for line in text.splitlines():
            if self.fence:
                self._inside_fence(line)
            else:
                self._outside_fence(line)
        return self.edits

    def _inside_fence(self, line):
        if line.rstrip() != self.fence:
            self.fenced.append(line)
            return
        self.edit.blocks[self.kind] = "\n".join(self.fenced)
        self.fence = ""

    def _outside_fence(self, line):
        heading = EDIT_HEADING.match(line)
        if heading:
            self.edit = Edit(heading.group(2), heading.group(3), len(heading.group(1)))
            self.edits.append(self.edit)
            return
        other = ANY_HEADING.match(line)
        if other and self.edit and len(other.group(1)) <= self.edit.level:
            self.edit = None
        if not self.edit:
            return
        opening = FENCE_OPEN.match(line)
        if opening:
            self.fence, self.kind, self.fenced = opening.group(1), opening.group(2), []
        elif FILE_LINE.match(line):
            self.edit.file = FILE_LINE.match(line).group(1).strip()
        elif TRACE_LINE.match(line):
            self.edit.traced = True


def splice(text, edit):
    """Apply one edit to `text`; return (new_text, problem)."""
    anchor = edit.anchor
    count = text.count(anchor)
    if count != 1:
        return text, f"anchor occurs {count} times (must be exactly once)"
    start = text.index(anchor)
    end = start + len(anchor)
    new = edit.blocks.get("new", "")
    if edit.operation == "insert":
        if end < len(text) and text[end] != "\n":
            return text, "an ~~~after anchor must end at the end of a line"
        return text[:end] + "\n" + new + text[end:], ""
    whole_lines = (start == 0 or text[start - 1] == "\n") and end < len(text) and text[end] == "\n"
    if not new and whole_lines:
        end += 1  # a deleted whole line takes its newline with it
    return text[:start] + new + text[end:], ""


def resolve(root, name):
    path = Path(name)
    return path if path.is_absolute() else root / path


def simulate(edits, root):
    """Apply edits in register order to in-memory copies; return (texts, rows)."""
    texts, rows = {}, []
    for edit in edits:
        problem = edit.shape_problem()
        path = resolve(root, edit.file) if edit.file else None
        if not problem and not path.is_file():
            problem = f"file not found: {path}"
        if not problem:
            texts.setdefault(path, path.read_text())
            texts[path], problem = splice(texts[path], edit)
        rows.append((edit, problem))
    return texts, rows


def report(rows):
    added = removed = problems = 0
    for edit, problem in rows:
        delta = edit.word_delta()
        added, removed = added + max(delta, 0), removed + max(-delta, 0)
        problems += bool(problem)
        note = problem or ("ok" if edit.traced else "ok (warning: no 'Traces to:' line)")
        print(f"{edit.edit_id:<6} {edit.status:<9} {edit.operation:<7} {edit.file:<40} {delta:+5d} words  {note}")
    files = len({edit.file for edit, _ in rows})
    print(f"net: {added - removed:+d} words (added {added}, removed {removed}) "
          f"across {files} file(s); {problems} problem(s)")
    return problems


def edits_check(register, root):
    edits = [e for e in RegisterParser().parse(register.read_text()) if e.status != "dropped"]
    _, rows = simulate(edits, root)
    return EXIT_PROBLEMS if report(rows) else 0


def agreed_edits(register):
    edits = RegisterParser().parse(register.read_text())
    pending = [e.edit_id for e in edits if e.status in ("proposed", "countered")]
    if pending:
        print(f"note: not agreed, left out: {', '.join(pending)}")
    return [e for e in edits if e.status == "agreed"]


def edits_apply(register, root):
    texts, rows = simulate(agreed_edits(register), root)
    if report(rows):
        print("nothing written: fix the problems above first", file=sys.stderr)
        return EXIT_PROBLEMS
    for path, text in texts.items():
        write_atomically(path, text)
    print(f"applied {len(rows)} edit(s) to {len(texts)} file(s)")
    return 0


def edits_verify(register, root):
    """After applying, by `edits apply` or any other route: every agreed text has landed."""
    edits = agreed_edits(register)
    all_new = "\n".join(e.blocks.get("new", "") for e in edits)
    problems = 0
    for edit in edits:
        path = resolve(root, edit.file)
        text = path.read_text() if path.is_file() else ""
        new = edit.blocks.get("new", "")
        missing_new = bool(new.strip()) and new not in text
        stale_old = edit.operation != "insert" and edit.anchor not in all_new and edit.anchor in text
        if missing_new or stale_old:
            problems += 1
            print(f"{edit.edit_id}: " + ("new text not found" if missing_new else "replaced text still present"))
    print(f"verified {len(edits) - problems} of {len(edits)} agreed edit(s)")
    return EXIT_PROBLEMS if problems else 0


# --- command line ----------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    st = sub.add_parser("status", help="show whose turn it is")
    st.add_argument("--board", type=Path, required=True)
    pub = sub.add_parser("publish", help="publish a full new board with a marker")
    pub.add_argument("--board", type=Path, required=True)
    pub.add_argument("--from", dest="draft", type=Path, required=True, help="full new board text")
    pub.add_argument("--expect-last", required=True, help="marker the board must end with now, or 'none'")
    pub.add_argument("--marker", required=True, help="marker to end the published board with")
    wt = sub.add_parser("wait", help="wait until the board ends with a marker (or DISCUSSION-CLOSED)")
    wt.add_argument("--board", type=Path, required=True)
    target = wt.add_mutually_exclusive_group(required=True)
    target.add_argument("--marker", help="e.g. 'END-OF-TURN 3 NEXT=CLAUDE'")
    target.add_argument("--after-round", type=int, help="group mode: wake on any round after this one")
    wt.add_argument("--timeout", type=int, default=540, help="seconds before giving up (exit 124)")
    wt.add_argument("--interval", type=int, default=20, help="seconds between checks")
    wt.add_argument("--settle", type=int, default=5, help="seconds to wait after the marker appears")
    sm = sub.add_parser("submit", help="group mode: store your submission for the open round")
    sm.add_argument("--board", type=Path, required=True)
    sm.add_argument("--round", type=int, required=True)
    sm.add_argument("--tag", required=True, help="your roster tag")
    sm.add_argument("--from", dest="draft", type=Path, required=True, help="your submission text")
    co = sub.add_parser("collect", help="group mode: wait for every rostered submission, or the deadline")
    co.add_argument("--board", type=Path, required=True)
    co.add_argument("--round", type=int, required=True)
    co.add_argument("--timeout", type=int, default=540, help="seconds this call may wait (exit 124)")
    co.add_argument("--interval", type=int, default=20, help="seconds between checks")
    ed = sub.add_parser("edits", help="check, apply or verify an edit register")
    ed.add_argument("action", choices=("check", "apply", "verify"))
    ed.add_argument("--register", type=Path, required=True, help="board.md or outcome.md holding the register")
    ed.add_argument("--root", type=Path, default=Path("."), help="folder that File: paths are relative to")
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "status":
        status(args.board)
    elif args.command == "publish":
        publish(args.board, args.draft, args.expect_last, args.marker)
    elif args.command == "wait":
        is_ready = exact_marker(args.marker) if args.marker else round_after(args.after_round)
        sys.exit(wait(args.board, is_ready, args.timeout, args.interval, args.settle))
    elif args.command == "submit":
        submit(args.board, args.round, args.tag, args.draft)
    elif args.command == "collect":
        sys.exit(collect(args.board, args.round, args.timeout, args.interval))
    else:
        action = {"check": edits_check, "apply": edits_apply, "verify": edits_verify}[args.action]
        sys.exit(action(args.register, args.root))


if __name__ == "__main__":
    main()
