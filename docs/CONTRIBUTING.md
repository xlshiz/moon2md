# 贡献指南

感谢你的贡献意愿！以下是一些指导原则。

## 开发环境

- Python 3.6+
- 无需第三方依赖（有意为之）
- 所有测试在 UTF-8 环境下进行

## 代码规范

1. **函数必须有 type hints + docstring**
   - Docstring 用中文或英文均可，需说明参数、返回值、用途
   - Type hints 覆盖所有参数和返回值

2. **零依赖原则**：不接受引入第三方 Python 包的 PR

3. **向后兼容**：解析逻辑不能破坏现有 mrexpt 文件的兼容性

## PR 流程

1. Fork 仓库
2. 创建 feature branch (`git checkout -b feat/xxx`)
3. 提交代码，确保 type hints 完整
4. 更新相关文档（USAGE.md / FORMAT.md 等）
5. 更新 CHANGELOG.md
6. 发起 Pull Request

## 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 使用 4 空格缩进
- 行宽不超过 100 字符
- import 分组：标准库 → 第三方 → 本地

## 测试

目前无自动化测试框架。提交前请手动验证：

```bash
# 用现有的 mrexpt 文件测试
python3 mrexpt2md.py test.mrexpt

# 需覆盖场景
# - 有批注的记录
# - 无批注的记录
# - 含 <BR> 换行的记录
# - 不同颜色的记录
# - 空文件 / 格式异常文件
```
