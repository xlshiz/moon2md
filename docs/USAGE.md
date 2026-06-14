# 使用指南

## 前置准备

1. **从静读天下导出 mrexpt 文件**

   在手机/平板上：
   1. 打开 Moon+ Reader
   2. 打开有高亮的书
   3. 点击屏幕中央 → 底部「章节目录」图标 ☰
   4. 切换到「书签」标签页
   5. 点击左下角「分享」图标 → 「导出列表到文件」
   6. 选择保存位置，将文件传到电脑

2. **环境要求**
   - Python 3.6+
   - 无需第三方依赖

## 基本用法

### 转换单个文件

```bash
python3 mrexpt2md.py 输入文件.mrexpt
```

将在同目录生成 `输入文件.md`。

### 指定输出路径

```bash
python3 mrexpt2md.py 输入文件.mrexpt 输出目录/笔记.md
```

### 查看帮助

```bash
python3 mrexpt2md.py
# 输出: 用法: python mrexpt2md.py <input.mrexpt> [output.md]
```

## 高级用法

### 批量转换所有 mrexpt

```bash
# 全部转成 Markdown
for f in *.mrexpt; do
    python3 mrexpt2md.py "$f"
done

# 归档到 notes 目录
mkdir -p notes
for f in *.mrexpt; do
    python3 mrexpt2md.py "$f" "notes/$(basename "$f" .mrexpt).md"
done
```

### 配合 Obsidian 使用

将生成的 `.md` 文件放入 Obsidian 仓库即可。Markdown 格式兼容 Obsidian：

```markdown
# 📖 书名
## 章节 X
> 高亮原文
*元信息行*
```

### 配合 Git 管理阅读笔记

```bash
git init
git add *.md
git commit -m "添加阅读笔记"
```

后续有新批注时重新导出 mrexpt 再转换，查看 diff 即可追踪笔记变更。

### 集成到笔记流水线

将以下脚本保存为 `sync-notes.sh`：

```bash
#!/bin/bash
# 静读天下笔记同步脚本
# 1. 将手机上导出的 .mrexpt 文件放到 ./exports/
# 2. 运行此脚本自动转换

mkdir -p notes
for f in exports/*.mrexpt; do
    name=$(basename "$f" .mrexpt)
    python3 mrexpt2md.py "$f" "notes/${name}.md"
    echo "✅ 已转换: ${name}"
done
```

## 输出格式说明

生成的 Markdown 文件结构如下：

```
# 📖 书名              ← 一级标题（书名）
                       
> 共 N 条高亮/批注      ← 统计信息
                       
---                      ← 分隔线
                       
## 章节 X               ← 二级标题（章节号）
                       
> 高亮原文              ← blockquote 引用
                       
**📝 批注：** 你的批注   ← 批注（仅当有批注时）
                       
*📍 位置: ... | 🏷️ 颜色 | 🕐 时间*  ← 斜体元信息
                       
---                      ← 分隔线
```

## 已知限制

| 限制 | 说明 | 解决方案 |
|------|------|----------|
| 无页码 | epub 无固定页码，使用章节+偏移 | 可配合书籍原文件交叉引用 |
| 特殊符号 | `￼` 等替换符无法还原为原始符号 | 这是原文件本身的限制 |
| 单色限制 | 当前工具支持所有颜色 | 如需过滤特定颜色可自行修改 |
| 仅支持 mrexpt | 不支持 .mrpro 备份格式 | 格式完全不同 |

## 故障排除

**问题：** 转换后高亮内容为空
**解决：** 检查 mrexpt 文件是否完整，确认第 12 行（索引 12）有内容。

**问题：** 颜色编码异常
**解决：** 确认颜色值为负整数。运行 `python3 -c "print(hex(0xFFFFFFFF + int('-28160') + 1))"` 校验。

**问题：** 中文乱码
**解决：** 确认使用 UTF-8 编码打开文件。脚本默认使用 `utf-8` 读写。
