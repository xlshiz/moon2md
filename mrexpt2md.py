#!/usr/bin/env python3
"""moon2md — Moon+ Reader (静读天下) 高亮/批注导出转换器。

将 .mrexpt 文件解析为结构化数据，输出为 Markdown 文档。

用法:
    python3 mrexpt2md.py <input.mrexpt> [output.md]

功能:
    - 解析 mrexpt 的 16 字段记录格式
    - 颜色编码自动转换（补码 → HEX → 中文名）
    - 毫秒时间戳转可读日期
    - <BR> 换行标签还原
    - 按章节组织 Markdown 输出

设计原则:
    - 零第三方依赖，仅用 Python 标准库
    - 输出兼容 Obsidian / Typora / GitHub Markdown
    - 纯函数式转换逻辑，易于测试和扩展
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# ── 常量 ────────────────────────────────────────────────────────

# 颜色码转换基数：32 位无符号整数上限 (0xFFFFFFFF)
_COLOR_BASE: int = 4294967295

# 已知颜色映射表（HEX → 中文描述）
_COLOR_PALETTE: Dict[str, str] = {
    'F50000': '🔴 红色',
    'FF0000': '🔴 红色',
    '00FF00': '🟢 绿色',
    '00BFFF': '🔵 蓝色',
    'FFFF00': '🟡 黄色',
    'FFA500': '🟠 橙色',
    'FF9200': '🟠 橙色（默认高亮）',
    'FF00FF': '🟣 紫色',
    '00FFFF': '🩵 青色',
    '808080': '⚪ 灰色',
    '000000': '⚫ 黑色',
}


# ── 类型别名 ────────────────────────────────────────────────────

Highlight = Dict[str, Any]
"""单条高亮记录，键:
    seq, book, chapter, location, length,
    color_hex, color_name, timestamp, note, text
"""


# ── 核心解析 ────────────────────────────────────────────────────

def parse_mrexpt(filepath: str) -> Tuple[str, List[Highlight]]:
    """解析 .mrexpt 文件，返回 (书名, 高亮列表)。

    文件结构:
        <元数据头 3 行>
        #
        <记录 1 的 16 行>
        #
        <记录 2 的 16 行>
        ...

    参数:
        filepath: .mrexpt 文件路径。

    返回:
        (book_name, highlights) 二元组。

    异常:
        FileNotFoundError: 文件不存在。
        ValueError: 文件格式异常（无有效记录）。
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f'文件不存在: {filepath}')

    with open(filepath, 'r', encoding='utf-8') as f:
        text: str = f.read()

    # 以 '#\n' 为分隔，第一块是元数据，后续每块是一条记录
    blocks: List[str] = text.split('\n#\n')
    raw_blocks: List[str] = blocks[1:]

    if not raw_blocks:
        raise ValueError(f'文件中未找到高亮记录: {filepath}')

    highlights: List[Highlight] = []
    for block in raw_blocks:
        lines: List[str] = block.strip().split('\n')
        if len(lines) < 16:
            # 不完整的记录，静默跳过
            continue

        highlight: Highlight = _parse_record(lines)
        highlights.append(highlight)

    if not highlights:
        raise ValueError(f'未能从文件中解析出有效记录: {filepath}')

    book_name: str = highlights[0]['book']
    return book_name, highlights


def _parse_record(lines: List[str]) -> Highlight:
    """从 16 行文本解析一条高亮记录。

    行索引映射:
        0:  序号
        1:  书名
        2:  文件路径（原始）
        3:  文件路径（小写）
        4:  章节号
        5:  未知 (通常为 '0')
        6:  章节内字符偏移
        7:  高亮长度
        8:  颜色编码（负整数，如 '-28160'）
        9:  时间戳（毫秒级）
        10: 未知标志 (通常为空)
        11: 批注/笔记内容（可为空）
        12: 高亮原文（可能含 <BR> 换行符）
        13: 未知标志 (通常为 '1')
        14: 未知标志 (通常为 '0')
        15: 未知标志 (通常为 '0')
    """
    seq: str = lines[0].strip()
    book: str = lines[1].strip()
    chapter: str = lines[4].strip()
    location: str = lines[6].strip()
    length: str = lines[7].strip()
    color_raw: str = lines[8].strip()
    ts_ms: str = lines[9].strip()
    note: str = lines[11].strip()
    text_raw: str = lines[12].strip()

    color_hex: str = _convert_color(color_raw)
    dt_str: str = _convert_timestamp(ts_ms)
    text_fixed: str = text_raw.replace('<BR>', '\n')
    color_name: str = _color_name_cn(color_hex)

    return {
        'seq': seq,
        'book': book,
        'chapter': chapter,
        'location': location,
        'length': length,
        'color_hex': color_hex,
        'color_name': color_name,
        'timestamp': dt_str,
        'note': note,
        'text': text_fixed,
    }


# ── 颜色处理 ────────────────────────────────────────────────────

def _convert_color(raw: str) -> str:
    """将 Moon+ Reader 的颜色编码转为 6 位 HEX 字符串。

    Moon+ Reader 使用 32 位补码表示颜色:
        hex = 0xFFFFFFFF + code + 1
    然后取低 24 位（后 6 位 HEX）。

    参数:
        raw: 颜色编码字符串，如 '-28160'。

    返回:
        6 位十六进制字符串，如 'ff9200'。
        解析失败时返回 '000000'。
    """
    try:
        val: int = int(raw)
        return str(hex(_COLOR_BASE + val + 1))[4:]
    except (ValueError, TypeError):
        return '000000'


def _color_name_cn(hex_str: str) -> str:
    """从 HEX 颜色值获取中文名称。

    参数:
        hex_str: 6 位十六进制颜色，如 'ff9200'。

    返回:
        中文描述，如 '🟠 橙色（默认高亮）'。
        未知颜色返回 '🎨 {HEX}'。
    """
    return _COLOR_PALETTE.get(hex_str.upper(), f'🎨 {hex_str}')


# ── 时间戳处理 ──────────────────────────────────────────────────

def _convert_timestamp(ms_str: str) -> str:
    """将毫秒级 Unix 时间戳转为可读日期。

    参数:
        ms_str: 毫秒时间戳字符串，如 '1671754358620'。

    返回:
        格式化日期字符串 'YYYY-MM-DD HH:MM:SS'。
        解析失败时原样返回输入。
    """
    try:
        ts: float = int(ms_str) / 1000.0
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return ms_str


# ── Markdown 输出 ───────────────────────────────────────────────

def to_markdown(
    book_name: str,
    highlights: List[Highlight],
    output_path: str,
) -> str:
    """将高亮数据渲染为 Markdown 文件。

    输出结构:
        # 📖 书名
        > 共 N 条高亮/批注
        ---
        ## 章节 X
        > 高亮原文
        **📝 批注：...**   (仅当有批注时)
        *📍 位置 ... | 🏷️ 颜色 | 🕐 时间*
        ---
        ...

    参数:
        book_name:  书名。
        highlights: 高亮记录列表。
        output_path: 输出文件路径。

    返回:
        写入的文件路径。
    """
    lines: List[str] = []
    _append_header(lines, book_name, len(highlights))

    current_chapter: Optional[str] = None
    for h in highlights:
        chapter: str = h['chapter']
        if chapter != current_chapter:
            current_chapter = chapter
            lines.append(f'## 章节 {chapter}')
            lines.append('')

        # 高亮原文（blockquote）
        text: str = h['text']
        for paragraph in text.split('\n'):
            lines.append(f'> {paragraph}')
        lines.append('')

        # 批注
        note: str = h['note']
        if note:
            lines.append(f'**📝 批注：** {note}')
            lines.append('')

        # 元信息行
        meta_parts: List[str] = [
            f'📍 位置: 章节 {h["chapter"]} · 偏移 {h["location"]}',
            f'🏷️ {h["color_name"]}',
            f'🕐 {h["timestamp"]}',
        ]
        lines.append(f'*{" | ".join(meta_parts)}*')
        lines.append('')
        lines.append('---')
        lines.append('')

    md_content: str = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return output_path


def _append_header(
    lines: List[str],
    book_name: str,
    count: int,
) -> None:
    """写入 Markdown 文件头信息。"""
    lines.append(f'# 📖 {book_name}')
    lines.append('')
    lines.append(f'> 共 {count} 条高亮/批注')
    lines.append('')
    lines.append('---')
    lines.append('')


# ── CLI 入口 ────────────────────────────────────────────────────

def main() -> None:
    """命令行入口。

    用法: python3 mrexpt2md.py <input.mrexpt> [output.md]

    如不指定 output，自动在同目录生成同名的 .md 文件。
    """
    if len(sys.argv) < 2:
        print('用法: python3 mrexpt2md.py <input.mrexpt> [output.md]')
        print('示例: python3 mrexpt2md.py 数学女孩3.mrexpt')
        sys.exit(1)

    input_path: str = sys.argv[1]
    output_path: str = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else os.path.splitext(input_path)[0] + '.md'
    )

    try:
        print(f'📂 读取: {input_path}')
        book_name, highlights = parse_mrexpt(input_path)
        print(f'📖 书名: {book_name}')
        print(f'🔢 条数: {len(highlights)}')
        out: str = to_markdown(book_name, highlights, output_path)
        print(f'✅ 已生成: {out}')
    except FileNotFoundError as e:
        print(f'❌ {e}', file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f'❌ 解析错误: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
