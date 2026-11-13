"""Copy an Examples excerpt from the symbol a guide names."""

MAX_LINES = 20


def excerpt(source_lines, start):
    """Return the symbol's lines from `start`, at most MAX_LINES of them."""
    body = source_lines[start:]
    return body[:MAX_LINES]
