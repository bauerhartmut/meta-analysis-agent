"""Evidence-based record verification.

The package is deliberately separate from the protected pooling module.  Its
only route into pooling is :mod:`research_agent.meta.verified_pool`.
"""

from .schema import SCHEMA_VERSION
from .workflow import build_verification, finalize_after_review
from .store import VerificationStore

__all__ = [
    "SCHEMA_VERSION", "VerificationStore", "build_verification",
    "finalize_after_review",
]
