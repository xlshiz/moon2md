# 设计文档

## 1. 概述

`moon2md`（Moon Reader to Obsidian-style Markdown）是一个轻量级 Python 工具，用于将 Moon+ Reader（静读天下）导出的高亮批注文件（`.mrexpt`）转换为结构清晰的 Markdown 文档。

### 设计目标

- **零依赖**：仅使用 Python 标准库，无需安装第三方包
- **保真转换**：完整保留原文、批注、颜色、时间等元信息
- **可读输出**：Markdown 输出可直接在 Obsidian、Typora、GitHub 等平台使用
- **可复用**：脚本设计为独立模块，可集成到其他工作流

## 2. 架构设计

### 2.1 模块结构

```
mrexpt2md.py
├── parse_mrexpt()      # 解析 mrexpt 文件
│   ├── convert_color()     # 颜色码转换
│   ├── convert_timestamp() # 时间戳转换
│   └── color_name_cn()    # 颜色中文名映射
├── to_markdown()       # 生成 Markdown
└── main()              # CLI 入口
```

### 2.2 数据流

```
.mrexpt 文件
    │
    ▼
parse_mrexpt()
    │ 按 '#' 分割条目
    │ 提取 16 个字段
    │ 转换颜色、时间戳
    ▼
highlights: list[dict]
    │ 每个 dict 包含：
    │   seq, book, chapter, location,
    │   length, color_hex, color_name,
    │   timestamp, note, text
    │
    ▼
to_markdown()
    │ 按章节分组
    │ 组装 Markdown 模板
    ▼
.md 文件
```

## 3. 字段映射

mrexpt 文件每条记录占用 16 行（索引 0-15）：

| 索引 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0 | seq | int | 序号 |
| 1 | book | str | 书名 |
| 2 | filepath | str | 原始文件路径 |
| 3 | filepath_lower | str | 小写路径 |
| 4 | chapter | int | 章节号 |
| 5 | unknown | int | 未知，通常为 0 |
| 6 | location | int | 章节内字符偏移 |
| 7 | length | int | 高亮文本长度 |
| 8 | color_code | int | 颜色编码（负整数） |
| 9 | timestamp_ms | int | 创建时间（毫秒时间戳） |
| 10 | flag | str | 空字符串 |
| 11 | note | str | 批注内容（可能为空） |
| 12 | text | str | 高亮原文（含 `<BR>` 换行） |
| 13-15 | extra | int | 额外标志，通常为 0 |

### 元数据（文件头部）

文件首 3 行为元数据：
- 第 1 行: `0` — 版本号
- 第 2 行: `indent:false` — 缩进设置
- 第 3 行: `trim:false` — 修剪设置

之后以 `#` 分隔每条高亮记录。

## 4. 关键算法

### 4.1 颜色转换

Moon+ Reader 使用**补码表示法**存储颜色：

```python
color_hex = hex(0xFFFFFFFF + color_code + 1)[4:]
```

例如 `-28160` → `0xFFFF9200` → `ff9200`（橙色）

这种表示方式将颜色值编码在 32 位无符号整数的低位中，高位全部置 1。

### 4.2 时间戳转换

时间戳为**毫秒级 Unix 时间戳**，转换为可读日期：

```python
datetime.fromtimestamp(ms_timestamp / 1000)
```

### 4.3 换行处理

高亮原文中的 `<BR>` 标签表示换行，直接替换为 `\n`。

## 5. 设计决策

### 5.1 为什么不用第三方库？

- `.mrexpt` 格式足够简单，手动解析即可
- 零依赖意味着在任何 Python 环境都能直接运行
- 减少维护负担

### 5.2 颜色中文名

使用硬编码映射表而非颜色值计算名称：颜色码解析后只能得到 RGB 值，硬编码映射表可以给出更直观的中文描述，也便于用户自定义。

### 5.3 按章节组织

原始数据按创建时间排序，但转换为按章节排序更利于阅读。由于 mrexpt 不包含绝对页码（epub 没有固定页码），使用章节号 + 字符偏移作为近似位置。

## 6. 扩展性

### 6.1 添加新输出格式

新增一个函数（如 `to_json()`、`to_csv()`）即可：

```python
def to_json(book_name, highlights, output_path):
    import json
    data = {"book": book_name, "highlights": highlights}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 6.2 自定义颜色映射

修改 `color_name_cn()` 函数的 `palette` 字典即可。

### 6.3 批量处理

脚本支持命令行参数，可结合 shell 脚本批量处理：

```bash
for f in *.mrexpt; do
    python3 mrexpt2md.py "$f" "notes/$(basename "$f" .mrexpt).md"
done
```
