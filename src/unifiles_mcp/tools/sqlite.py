"""SQLite database operation tools.

This module contains SQLite-related MCP tools.
"""

import json
from typing import Annotated, Any, cast

import unifiles
from mcp.server.fastmcp import Context
from pydantic import Field

from ..utils import async_wrapper, validators


# Internal implementation functions (for testing)
async def _sqlite_inspect_database_impl(
    db_path: str,
    include_preview: bool,
    preview_rows: int,
    ctx: Context,
) -> dict[str, Any]:
    """检查 SQLite 数据库结构（内部实现）。"""
    await ctx.info(f"开始检查 SQLite 数据库: {db_path}")

    try:
        validated_path = validators.validate_file_path(db_path, must_exist=True)

        info = await async_wrapper.to_async(
            unifiles.get_database_info,
            str(validated_path),
            include_preview,
            preview_rows,
        )

        await ctx.info(f"成功检查数据库: {db_path}, " f"表数量: {info.get('table_count', 0)}")
        return cast(dict[str, Any], info)

    except FileNotFoundError as e:
        await ctx.error(f"数据库文件不存在: {db_path}")
        raise ValueError(f"数据库文件不存在: {db_path}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取数据库时出错: {e}")
        raise ValueError(f"读取数据库失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"检查数据库时发生未知错误: {e}")
        raise ValueError(f"检查数据库失败: {str(e)}") from e


async def _sqlite_get_schema_impl(
    db_path: str,
    table_name: str,
    ctx: Context,
) -> dict[str, str]:
    """获取 SQLite 表结构（内部实现）。"""
    await ctx.info(f"开始获取表结构: {db_path}, 表名: {table_name}")

    try:
        validated_path = validators.validate_file_path(db_path, must_exist=True)

        schema = await async_wrapper.to_async(
            unifiles.get_schema,
            str(validated_path),
            table_name,
        )

        await ctx.info(f"成功获取表结构: {table_name}, " f"字段数: {len(schema)}")
        return cast(dict[str, str], schema)

    except FileNotFoundError as e:
        await ctx.error(f"数据库文件不存在: {db_path}")
        raise ValueError(f"数据库文件不存在: {db_path}") from e
    except ValueError as e:
        await ctx.error(f"参数错误: {e}")
        raise ValueError(f"获取表结构失败: {str(e)}") from e
    except unifiles.FileReadError as e:
        await ctx.error(f"读取数据库时出错: {e}")
        raise ValueError(f"读取数据库失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"获取表结构时发生未知错误: {e}")
        raise ValueError(f"获取表结构失败: {str(e)}") from e


async def _sqlite_query_impl(
    db_path: str,
    sql: str,
    query_params: dict[str, Any] | list[Any] | None,
    ctx: Context,
) -> str:
    """执行 SQL 查询并返回 JSON 格式的数据（内部实现）。"""
    await ctx.info(f"开始执行 SQL 查询: {db_path}, SQL: {sql[:50]}...")

    try:
        validated_path = validators.validate_file_path(db_path, must_exist=True)

        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("仅支持 SELECT 查询，不允许修改数据")

        params_arg: dict[str, Any] | list[Any] | tuple[Any, ...] | None = (
            tuple(query_params) if isinstance(query_params, list) else query_params
        )

        df = await async_wrapper.to_async(
            unifiles.query,
            str(validated_path),
            sql,
            params_arg,
        )

        df_filled = df.fillna(value=None)
        result = df_filled.to_dict("records")

        await ctx.info(f"成功执行查询: {db_path}, " f"返回行数: {len(result)}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except FileNotFoundError as e:
        await ctx.error(f"数据库文件不存在: {db_path}")
        raise ValueError(f"数据库文件不存在: {db_path}") from e
    except ValueError as e:
        await ctx.error(f"查询错误: {e}")
        raise ValueError(f"查询失败: {str(e)}") from e
    except Exception as e:
        await ctx.error(f"执行查询时发生错误: {e}")
        raise ValueError(f"执行查询失败: {str(e)}") from e


# MCP tool functions (registered by main)
async def sqlite_inspect_database(
    db_path: Annotated[
        str,
        Field(description="SQLite 数据库文件路径（支持相对路径和绝对路径）"),
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
            description="如果 include_preview=True，每个表预览的行数（默认 3 行）",
        ),
    ] = 3,
) -> dict[str, Any]:
    """检查 SQLite 数据库结构。

    返回包含所有表名称、表结构和前几行数据预览的摘要信息。
    在决定查询哪个表之前，请先使用此工具。
    """
    return await _sqlite_inspect_database_impl(db_path, include_preview, preview_rows, ctx)


async def sqlite_get_schema(
    db_path: Annotated[
        str,
        Field(description="SQLite 数据库文件路径（支持相对路径和绝对路径）"),
    ],
    table_name: Annotated[str, Field(description="表名")],
    ctx: Context,
) -> dict[str, str]:
    """获取 SQLite 表结构（字段名到字段类型的映射）。

    核心工具。LLM 写 SQL 前必须看 Schema。
    """
    return await _sqlite_get_schema_impl(db_path, table_name, ctx)


async def sqlite_query(
    db_path: Annotated[
        str,
        Field(description="SQLite 数据库文件路径（支持相对路径和绝对路径）"),
    ],
    sql: Annotated[str, Field(description="SQL 查询语句（仅支持 SELECT 查询）")],
    ctx: Context,
    params: Annotated[
        dict[str, Any] | list[Any] | None,
        Field(
            description="查询参数（可选）。dict 用于 :name 占位符，list/tuple 用于 ? 占位符",
        ),
    ] = None,
) -> str:
    """执行 SQL 查询并返回 JSON 格式的数据。

    支持参数化查询，防止 SQL 注入。仅支持 SELECT 查询。
    """
    return await _sqlite_query_impl(db_path, sql, params, ctx)


def register(server: Any) -> None:
    """Register SQLite tools on the given FastMCP server."""
    server.tool()(sqlite_inspect_database)
    server.tool()(sqlite_get_schema)
    server.tool()(sqlite_query)
