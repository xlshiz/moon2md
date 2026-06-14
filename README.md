# moon2md 📖→📝

**Moon+ Reader（静读天下）高亮/批注导出工具**

将 `.mrexpt` 文件一键转为可读、可整理的 **Markdown** 笔记。

## 快速开始

```bash
python3 mrexpt2md.py 你的书.mrexpt
```

生成同名的 `.md` 文件，按章节组织，开箱即用。

## 功能

| 特性 | 说明 |
|------|------|
| ✅ 解析 mrexpt | 提取书名、原文、批注、颜色、时间…… |
| ✅ 按章节组织 | 自动分组，结构清晰 |
| ✅ 颜色中文名 | `FF9200` → `🟠 橙色（默认高亮）` |
| ✅ 时间转日期 | `1671754358620` → `2022-12-23 08:12:38` |
| ✅ `<BR>` 换行 | 自动还原为 `\n` |
| ✅ 零依赖 | 纯 Python 3，无需 pip install |
| ✅ 兼容 Obsidian | 输出 Markdown 可直接放入 Obsidian 仓库 |

## 项目结构

```
moon2md/
├── mrexpt2md.py            ← 转换脚本（可独立运行）
├── pyproject.toml           ← 可 pip install 安装
├── LICENSE                  ← MIT 许可证
├── .gitignore
├── docs/
│   ├── DESIGN.md            ← 设计文档（架构、算法、扩展）
│   ├── USAGE.md             ← 使用指南（批量/Obsidian/Git 集成）
│   ├── FORMAT.md            ← .mrexpt 格式逆向工程说明
│   ├── CHANGELOG.md         ← 更新日志
│   ├── CONTRIBUTING.md      ← 贡献指南
│   └── TODO.md              ← 待办 & 规划
└── *.mrexpt / *.md          ← 源文件 + 生成文件
```

## 详细文档

| 文档 | 内容 |
|------|------|
| [docs/DESIGN.md](docs/DESIGN.md) | 架构设计、数据流图、算法说明 |
| [docs/USAGE.md](docs/USAGE.md) | 从导出到转换的完整操作流程 |
| [docs/FORMAT.md](docs/FORMAT.md) | mrexpt 文件格式完整规范 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 版本历史 |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | 参与开发的指引 |
| [docs/TODO.md](docs/TODO.md) | 未来计划 |

## 系统要求

- Python 3.6+
- 无第三方依赖
