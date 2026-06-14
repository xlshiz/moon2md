# 更新日志

## v0.1.0 (2026-06-07)

### ✨ 初始版本

- 实现 mrexpt 文件解析引擎
- 支持字段：序号、书名、章节、位置、长度、颜色、时间戳、批注、高亮原文
- 颜色编码自动转换（补码 → HEX → 中文名）
- 毫秒时间戳 → 可读日期
- `<BR>` 换行标签还原
- 按章节组织的 Markdown 输出
- 零依赖：仅使用 Python 标准库
- 完整的文档体系：
  - README、DESIGN、USAGE、FORMAT、CHANGELOG、CONTRIBUTING、TODO
  - LICENSE (MIT)
  - 脚本内部全量 type hints + docstring
