# MSTR User Lowercase Script

这个仓库提供一个通过 `mstrio-py` 批量检查并小写化 MicroStrategy / Strategy One 用户信息的交互式脚本。

脚本会执行以下流程：

1. 登录指定的 Library URL。
2. 列出当前平台全部用户。
3. 将用户清单导入 Pandas DataFrame。
4. 筛选用户名、显示名、登录 ID 或受信任验证请求用户 ID 中包含大写字母的用户。
5. 识别可能的 MSTR 平台自带用户，并询问是否剔除，默认剔除。
6. 列出剩余待处理用户和数量，要求操作用户确认。
7. 将显示名、登录 ID、受信任验证请求用户 ID 改为对应小写，数字保持不变。
8. 返回每个用户的执行结果。
9. 再次列出当前平台用户并检查是否仍有目标大写用户。
10. 成功时输出批处理脚本运行成功的祝贺信息。

## 安装依赖

建议使用 Python 3.10 或更高版本。新版 `mstrio-py` 在 PyPI 上要求 Python `>=3.10,<3.14`。

```bash
pip install -r requirements.txt
```

## 配置连接信息

推荐使用环境变量，避免把真实密码提交到 Git：

```bash
export MSTR_LIBRARY_URL="https://your-library.example.com/MicroStrategyLibrary"
export MSTR_USERNAME="Administrator"
export MSTR_PASSWORD="your-password"
```

也可以直接编辑 `mstr_user_lowercase.py` 顶部的 `CONFIG` 配置区，将占位符替换成你的 Library URL、用户名和密码。

## 推荐运行方式：Notebook

推荐使用 Notebook 逐步执行、逐步确认：

```bash
jupyter notebook mstr_user_lowercase_notebook.ipynb
```

Notebook 会按 cell 拆分流程：登录、列出用户、筛选大写用户、确认是否剔除平台自带用户、预览变更、最终执行、复查结果。

## 命令行运行

```bash
python mstr_user_lowercase.py
```

如需先预演、不真正修改平台用户：

```bash
python mstr_user_lowercase.py --dry-run
```

如果确认环境无误，也可以跳过最终确认：

```bash
python mstr_user_lowercase.py --yes
```

## 注意事项

- 建议先在测试环境运行。
- 脚本会在修改前检查小写化后的登录 ID 是否与现有用户或本批次其他用户冲突；发现冲突会停止执行。
- 默认会剔除疑似平台自带用户，例如 `Administrator`、`Guest`、`Public / Guest`、`System Administrator` 等。
- `mstrio-py` 中 `User.alter(username=...)` 用于修改用户登录名，`full_name` 用于修改用户显示/全名，`trust_id` 用于修改受信任认证 ID。
