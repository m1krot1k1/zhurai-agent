"""Shared path validation helpers for tool implementations.

Extracts the ``resolve() + relative_to()`` and ``..`` traversal check
patterns previously duplicated across skill_manager_tool, skills_tool,
skills_hub, cronjob_tools, and credential_files.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_within_dir(path: Path, root: Path) -> str | None:
    """Ensure *path* resolves to a location within *root*.

    Returns an error message string if validation fails, or ``None`` if the
    path is safe.  Uses ``Path.resolve()`` to follow symlinks and normalize
    ``..`` components.

    Usage::

        error = validate_within_dir(user_path, allowed_root)
        if error:
            return json.dumps({"error": error})
    """
    try:
        resolved = path.resolve()
        root_resolved = root.resolve()
        resolved.relative_to(root_resolved)
    except (ValueError, OSError) as exc:
        return f"Path escapes allowed directory: {exc}"
    return None


def has_traversal_component(path_str: str) -> bool:
    """Return True if *path_str* contains ``..`` traversal components.

    Checks for ``..`` after normalizing whitespace to catch bypasses like
    ``".. /foo"`` (space before slash) or ``"..\\foo"``.

    This is a fast pre-filter before ``validate_within_dir()`` does the
    full ``Path.resolve()`` round-trip.  It is intentionally conservative:
    any path component that strips to ``..`` is flagged, even if a later
    resolution step would normalise it away.
    """
    parts = Path(path_str).parts
    # Strip whitespace from each component before comparison — catches
    # traversal-bypass patterns like ``".. "`` (trailing space), ``" .."``
    # (leading space), and equivalents via normpath / os.sep confusion.
    return any(part.strip() == ".." for part in parts)
