"""Excel file operation tools.

This module contains Excel-related MCP tools.
"""

import json
from typing import Annotated, Any, cast

import unifiles
from mcp.server.fastmcp import Context
from pydantic import Field

from ..utils import async_wrapper, validators


# Internal implementation functions (for testing)
async def _excel_inspect_file_impl(
    file_path: str,
    include_preview: bool,
    preview_rows: int,
    ctx: Context,
) -> dict[str, Any]:
    """检查 Excel 文件结构（内部实现）。

    返回包含所有 Sheet 名称、列头和前几行数据预览的摘要信息。
    在决定读取哪个 Sheet 之前，请先使用此工具。

    Args:
        file_path: 文件路径
        include_preview: 是否包含数据预览
        preview_rows: 每个工作表预览的行数
        ctx: FastMCP Context 对象

    Returns:
        包含文件信息的字典

    Raises:
        ValueError: 如果文件路径无效或文件不存在
        FileReadError: 如果读取文件时发生错误
    """
    await ctx.info(f"开始检查 Excel 文件: {file_path}")

    try:
        validated_path = validators.validate_file_path(file_path, must_exist=True)

        info = await async_wrapper.to_async(
            unifiles.get_excel_info,
            str(validated_path),
            include_preview,
            preview_rows,
        )

        await ctx.info(f"成功检查文件: {file_path}, " f"工作表数量: {info.get('sheet_count', 0)}")
        return cast(dict[str, Any], info)

    except FileNotFoundError as e:
        await ctx.error(f"文件不存在: {file_path}")
        raise ValueError(f"文件不存在: {file_path}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取文件时出错: {e}")
        raise ValueError(f"读取文件失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"检查文件时发生未知错误: {e}")
        raise ValueError(f"检查文件失败: {str(e)}") from e


async def _excel_read_sheet_impl(
    file_path: str,
    sheet_name: str | int | None,
    ctx: Context,
) -> str:
    """读取 Excel 工作表内容并返回 JSON 格式的数据（内部实现）。"""
    await ctx.info(f"开始读取 Excel 工作表: {file_path}, sheet: {sheet_name}")

    try:
        validated_path = validators.validate_file_path(file_path, must_exist=True)

        df = await async_wrapper.to_async(
            unifiles.read_excel,
            str(validated_path),
            sheet_name,
        )

        import numpy as np

        df_filled = df.fillna(value=None).replace({np.nan: None})

        result = df_filled.to_dict("records")

        def clean_nan(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            elif isinstance(obj, float) and (obj != obj):
                return None
            return obj

        result = clean_nan(result)

        await ctx.info(
            f"成功读取工作表: {file_path}, " f"行数: {len(result)}, 列数: {len(df.columns)}"
        )

        return json.dumps(result, ensure_ascii=False, indent=2)

    except FileNotFoundError as e:
        await ctx.error(f"文件不存在: {file_path}")
        raise ValueError(f"文件不存在: {file_path}") from e
    except ValueError as e:
        await ctx.error(f"参数错误: {e}")
        raise ValueError(f"读取失败: {str(e)}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取文件时出错: {e}")
        raise ValueError(f"读取文件失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"读取工作表时发生未知错误: {e}")
        raise ValueError(f"读取工作表失败: {str(e)}") from e


# MCP tool functions (registered by main)
async def excel_inspect_file(
    file_path: Annotated[
        str,
        Field(description="Excel 文件路径（支持相对路径和绝对路径）"),
    ],
    ctx: Context,
    include_preview: Annotated[
        bool,
        Field(
            description="是否包含数据预览（默认 False，避免数据量大时性能问题）",
        ),
    ] = False,
    preview_rows: Annotated[
        int,
        Field(
            description="如果 include_preview=True，每个工作表预览的行数（默认 3 行）",
        ),
    ] = 3,
) -> dict[str, Any]:
    """检查 Excel 文件结构。

    返回包含所有 Sheet 名称、列头和前几行数据预览的摘要信息。
    在决定读取哪个 Sheet 之前，请先使用此工具。
    """
    return await _excel_inspect_file_impl(file_path, include_preview, preview_rows, ctx)


async def excel_read_sheet(
    file_path: Annotated[
        str,
        Field(description="Excel 文件路径（支持相对路径和绝对路径）"),
    ],
    ctx: Context,
    sheet_name: Annotated[
        str | int | None,
        Field(
            description="工作表名称或索引，None 表示读取第一个工作表",
        ),
    ] = None,
) -> str:
    """读取 Excel 工作表内容并返回 JSON 格式的数据。

    支持读取单个工作表。如果数据量大，返回结果可能被截断。
    """
    return await _excel_read_sheet_impl(file_path, sheet_name, ctx)


def register(server: Any) -> None:
    """Register Excel tools on the given FastMCP server."""
    server.tool()(excel_inspect_file)
    server.tool()(excel_read_sheet)
