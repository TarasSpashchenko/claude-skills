"""Merge newly generated Task Routing rows into the existing AGENTS.md table."""


def row_key(row):
    return row["category"].strip().lower()


def merge_rows(old_rows, new_rows):
    """New rows first; an old row stays when no new row has its category."""
    new_keys = {row_key(r) for r in new_rows}
    kept = [r for r in old_rows if row_key(r) not in new_keys]
    return new_rows + kept
