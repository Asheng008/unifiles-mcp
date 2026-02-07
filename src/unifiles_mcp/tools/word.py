"""Word document operation tools.

This module contains Word-related MCP tools.
"""

from typing import Annotated, Any, cast

import unifiles
from mcp.server.fastmcp import Context
from pydantic import Field

from ..utils import async_wrapper, validators


# Internal implementation function (for testing)
async def _word_read_document_impl(
    file_path: str,
    ctx: Context,
) -> str:
    """读取 Word 文档内容（内部实现）。

    读取 Word (.docx) 文档的全部文本内容，段落之间用换行符分隔。

    Args:
        file_path: Word 文档路径
        ctx: FastMCP Context 对象

    Returns:
        文档的文本内容（字符串，段落之间用换行符分隔）

    Raises:
        ValueError: 如果文件路径无效、文件不存在或文件格式不支持
        FileReadError: 如果读取文件时发生错误
    """
    await ctx.info(f"开始读取 Word 文档: {file_path}")

    try:
        # 验证文件路径
        validated_path = validators.validate_file_path(file_path, must_exist=True)

        # 检查文件扩展名（可选，但有助于提前发现错误）
        if not str(validated_path).lower().endswith(".docx"):
            await ctx.warning(f"文件扩展名不是 .docx: {file_path}。unifiles 仅支持 .docx 格式。")

        # 异步调用 unifiles.read_docx
        text = await async_wrapper.to_async(
            unifiles.read_docx,
            str(validated_path),
        )

        # 统计文本信息
        text_length = len(text)
        paragraph_count = text.count("\n") + 1 if text else 0

        await ctx.info(
            f"成功读取 Word 文档: {file_path}, "
            f"文本长度: {text_length} 字符, 段落数: {paragraph_count}"
        )

        return cast(str, text)

    except FileNotFoundError as e:
        await ctx.error(f"文件不存在: {file_path}")
        raise ValueError(f"文件不存在: {file_path}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取文件时出错: {e}")
        raise ValueError(f"读取文件失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"读取文档时发生未知错误: {e}")
        raise ValueError(f"读取文档失败: {str(e)}") from e


# MCP tool function (registered by main)
async def word_read_document(
    file_path: Annotated[
        str,
        Field(description="Word 文档路径（支持相对路径和绝对路径，仅支持 .docx 格式）"),
    ],
    ctx: Context,
) -> str:
    """读取 Word 文档内容。

    读取 Word (.docx) 文档的全部文本内容，段落之间用换行符分隔。
    """
    return await _word_read_document_impl(file_path, ctx)


def register(server: Any) -> None:
    """Register Word tools on the given FastMCP server."""
    server.tool()(word_read_document)
