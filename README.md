# MSTR User Lowercase Notebook

这个仓库提供一个通过 `mstrio-py` 批量检查并小写化 MicroStrategy / Strategy One 用户信息的交互式 Notebook。

推荐把 [mstr_user_lowercase_notebook.ipynb](./mstr_user_lowercase_notebook.ipynb) 作为唯一执行入口。Notebook 已经集成全部业务逻辑，不再需要单独运行 `.py` 脚本。

Notebook 会执行以下流程：

1. 登录指定的 Library URL。
2. 列出当前平台全部用户。
3. 将用户清单导入 Pandas DataFrame。
4. 筛选用户名、显示名、登录 ID 或受信任验证请求用户 ID 中包含大写字母的用户。
5. 默认剔除疑似 MSTR 平台自带用户，并列出可处理用户编号。
6. 由执行人输入单个编号、编号组，或 `all` 来决定实际处理范围。
7. 将显示名、登录 ID、受信任验证请求用户 ID 改为对应小写，数字保持不变。
8. 返回每个用户的执行结果。
9. 再次列出当前平台用户并检查是否仍有目标大写用户。
10. 成功时输出批处理脚本运行成功的祝贺信息。

详细部署、执行和交接说明请阅读 [KT 文档](./docs/KT_MSTR_USER_LOWERCASE.md)。

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

## 运行 Notebook

```bash
jupyter notebook mstr_user_lowercase_notebook.ipynb
```

Notebook 会按 cell 拆分流程。第 5 步会要求执行人输入编号，例如 `1`、`1;3;5` 或 `all`，第 7 步会根据输入编号实际修改用户。

## 注意事项

- 建议先在测试环境运行。
- Notebook 会在修改前检查小写化后的登录 ID 是否与现有用户或本批次其他用户冲突；发现冲突会停止执行。
- 默认会剔除疑似平台自带用户，例如 `Administrator`、`Guest`、`Public / Guest`、`System Administrator` 等。
- `mstrio-py` 中 `User.alter(username=...)` 用于修改用户登录名，`full_name` 用于修改用户显示/全名，`trust_id` 用于修改受信任认证 ID。
