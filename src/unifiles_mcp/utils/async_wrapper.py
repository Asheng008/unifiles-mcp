"""Async wrapper utilities for unifiles-mcp."""

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def to_async(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Wrap a synchronous function to run in a thread pool.

    Args:
        func: The synchronous function to wrap
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The result of the function call
    """
    return await asyncio.to_thread(func, *args, **kwargs)
