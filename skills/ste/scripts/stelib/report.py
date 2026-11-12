"""Write the results of `ste.py check` as text or JSON, and select the exit code."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from .checks import ERROR, QUESTION, UNKNOWN_WORD_RULE, Finding

MAX_LISTED_LINES = 12
MAX_LISTED_UNKNOWN_WORDS = 80
EXIT_CLEAN = 0
EXIT_ERRORS = 1
EXIT_INCOMPLETE = 2


@dataclass
class FileReport:
    path: str
    kind: str = ""
    scope: str = "all sentences"
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)  # what the check could not do
    complete: bool = True
    config: str | None = None

    def count(self, cls: str) -> int:
        return sum(1 for finding in self.findings if finding.cls == cls)


def _line_list(lines: list[int]) -> str:
    shown = ", ".join(str(number) for number in lines[:MAX_LISTED_LINES])
    return shown + (", ..." if len(lines) > MAX_LISTED_LINES else "")


def format_finding(path: str, finding: Finding) -> str:
    line = f"{path}:{finding.line}:{finding.column}: {finding.cls} {finding.rule} {finding.message}"
    if finding.count > 1:
        line += f" [{finding.count} times, lines {_line_list(finding.lines)}]"
    if finding.alternatives:
        line += f" -> {finding.alternatives}"
    if finding.page:
        line += f" (p. {finding.page})"
    return line


def format_text(reports: list[FileReport]) -> str:
    lines = []
    for report in reports:
        config = report.config or "none"
        lines.append(f"# {report.path}: kind {report.kind or '?'}, {report.scope}, config {config}")
        lines += [f"# NOT COMPLETE: {note}" for note in report.notes]
        unknown = [f for f in report.findings if f.rule == UNKNOWN_WORD_RULE]
        lines += [format_finding(report.path, f) for f in report.findings if f.rule != UNKNOWN_WORD_RULE]
        if unknown:
            lines.append(_unknown_words_line(report.path, unknown))
    lines.append(_summary(reports))
    return "\n".join(lines)


def _totals(reports: list[FileReport], cls: str) -> str:
    """For example "12 errors (8.1: 7, 6.3: 5)"."""
    by_rule: dict[str, int] = {}
    for report in reports:
        for finding in report.findings:
            if finding.cls == cls:
                by_rule[finding.rule] = by_rule.get(finding.rule, 0) + 1
    total = sum(by_rule.values())
    detail = ", ".join(f"{rule}: {count}" for rule, count in sorted(by_rule.items(), key=lambda i: -i[1]))
    return f"{total} {cls}s" + (f" ({detail})" if detail else "")


def _summary(reports: list[FileReport]) -> str:
    complete = "" if all(r.complete for r in reports) else ", check NOT complete"
    return (f"# {_totals(reports, ERROR)}, {_totals(reports, QUESTION)} "
            f"in {len(reports)} file(s){complete}")


def _unknown_words_line(path: str, findings: list[Finding]) -> str:
    """One line for all the words that are not in the dictionary."""
    shown = findings[:MAX_LISTED_UNKNOWN_WORDS]
    words = ", ".join(f"{f.text} ({f.line}" + (f", {f.count} times)" if f.count > 1 else ")")
                      for f in shown)
    if len(findings) > len(shown):
        words += f", and {len(findings) - len(shown)} more words (use --json for all)"
    first = findings[0]
    return (f"{path}:{first.line}:{first.column}: question {UNKNOWN_WORD_RULE} not in the dictionary. "
            "Keep a word only if it is a technical noun or a technical verb (rules 1.5, 1.12), "
            f"and add it to .ste.toml: {words}")


def format_json(reports: list[FileReport]) -> str:
    return json.dumps({
        "complete": all(report.complete for report in reports),
        "files": [asdict(report) for report in reports],
    }, indent=2, ensure_ascii=False)


def exit_code(reports: list[FileReport]) -> int:
    if not all(report.complete for report in reports):
        return EXIT_INCOMPLETE
    if any(report.count(ERROR) for report in reports):
        return EXIT_ERRORS
    return EXIT_CLEAN
