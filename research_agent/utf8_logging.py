"""
UTF-8-safe logging helpers.

When stdout/stderr use a narrow codec such as cp1252 (Windows consoles), a log
message containing e.g. '\\u2192' ('\u2192') raises UnicodeEncodeError inside the
logging handler and Python silently drops the record, so errors "look like
nothing happened". Reconfiguring the streams to UTF-8 with errors='replace'
lets logging never crash regardless of which module emits Unicode text.
"""

import sys
import logging


def utf8_stream(stream):
    """Reconfigure a text stream (or stdio wrapper) for UTF-8 with replacement."""
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError):
            pass
    return stream


class Utf8StreamHandler(logging.StreamHandler):
    """StreamHandler that never lets a write failure kill the process/thread.

    logging.StreamHandler.handleError already keeps the handler alive; this
    additionally guards the error report itself so a bad console pipe cannot
    raise out of the logging call.
    """

    def handleError(self, record):
        try:
            super().handleError(record)
        except Exception:
            pass


def make_utf8_stream_handler(stream=None):
    """Build a UTF-8-safe StreamHandler over the given stream (default stdout)."""
    return Utf8StreamHandler(utf8_stream(stream or sys.stdout))


def ensure_utf8():
    """Reconfigure process stdout/stderr for UTF-8-safe logging."""
    utf8_stream(sys.stdout)
    utf8_stream(sys.stderr)