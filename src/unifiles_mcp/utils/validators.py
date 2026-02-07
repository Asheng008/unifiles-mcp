"""Validation utilities for unifiles-mcp."""

from pathlib import Path


def validate_file_path(file_path: str | Path, must_exist: bool = True) -> Path:
    """Validate and normalize a file path.

    Args:
        file_path: The file path to validate
        must_exist: Whether the file must exist

    Returns:
        Normalized Path object

    Raises:
        ValueError: If the path is invalid or not allowed
        FileNotFoundError: If must_exist is True and the file doesn't exist
    """
    file_path_str = str(file_path)

    # Check for path traversal attacks BEFORE resolving
    # This catches "../" patterns in the original path
    if ".." in file_path_str:
        raise ValueError(f"Path traversal detected: {file_path}")

    path = Path(file_path).resolve()

    # Check if file exists (if required)
    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path


def validate_page_range(
    page_range: tuple[int, int] | None,
    total_pages: int | None = None,
) -> tuple[int, int] | None:
    """Validate page range.

    Args:
        page_range: Page range tuple (start, end), 1-based
        total_pages: Total number of pages (for validation)

    Returns:
        Validated page range or None

    Raises:
        ValueError: If the page range is invalid
    """
    if page_range is None:
        return None

    start, end = page_range

    # Validate range
    if start < 1:
        raise ValueError(f"Start page must be >= 1, got {start}")
    if end < start:
        raise ValueError(f"End page ({end}) must be >= start page ({start})")

    # Validate against total pages if provided
    if total_pages is not None:
        if end > total_pages:
            raise ValueError(f"End page ({end}) exceeds total pages ({total_pages})")

    return page_range
