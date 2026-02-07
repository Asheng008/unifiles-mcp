"""PDF file operation tools.

This module contains PDF-related MCP tools.
"""

from typing import Annotated, Any, cast

import unifiles
from mcp.server.fastmcp import Context
from pydantic import Field

from ..utils import async_wrapper, validators


# Internal implementation function (for testing)
async def _pdf_extract_text_impl(
    file_path: str,
    page_range: tuple[int, int] | list[int] | None,
    ctx: Context,
) -> str:
    """从 PDF 文件中提取文本内容（内部实现）。"""
    await ctx.info(f"开始提取 PDF 文本: {file_path}")

    try:
        validated_path = validators.validate_file_path(file_path, must_exist=True)

        # 兼容 JSON 传来的 list，转为 tuple
        if page_range is not None and isinstance(page_range, list):
            page_range = tuple(page_range)  # type: ignore[assignment]
        if page_range is not None:
            validators.validate_page_range(
                cast(tuple[int, int] | None, page_range), total_pages=None
            )

        text = await async_wrapper.to_async(
            unifiles.extract_text,
            str(validated_path),
            page_range,
        )

        text_length = len(text)
        line_count = text.count("\n") + 1 if text else 0

        await ctx.info(
            f"成功提取 PDF 文本: {file_path}, " f"文本长度: {text_length} 字符, 行数: {line_count}"
        )

        return cast(str, text)

    except FileNotFoundError as e:
        await ctx.error(f"文件不存在: {file_path}")
        raise ValueError(f"文件不存在: {file_path}") from e
    except ValueError as e:
        await ctx.error(f"参数错误: {e}")
        raise ValueError(f"提取失败: {str(e)}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取文件时出错: {e}")
        raise ValueError(f"读取文件失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"提取文本时发生未知错误: {e}")
        raise ValueError(f"提取文本失败: {str(e)}") from e


# MCP tool function (registered by main)
async def pdf_extract_text(
    file_path: Annotated[
        str,
        Field(description="PDF 文件路径（支持相对路径和绝对路径）"),
    ],
    ctx: Context,
    page_range: Annotated[
        tuple[int, int] | list[int] | None,
        Field(
            description="页码范围 (start, end)，1-based，None 表示提取所有页面。例如 [1, 5] 表示第 1 到第 5 页",
        ),
    ] = None,
) -> str:
    """从 PDF 文件中提取文本内容。

    支持提取所有页面或指定页面范围的文本。页面之间用换行符分隔。
    """
    return await _pdf_extract_text_impl(file_path, page_range, ctx)


def register(server: Any) -> None:
    """Register PDF tools on the given FastMCP server."""
    server.tool()(pdf_extract_text)
