# KT 文档：MSTR 用户批量小写化 Notebook

## 1. 交接目标

本文档用于指导执行团队部署并运行 `mstr_user_lowercase_notebook.ipynb`，通过 `mstrio-py` 连接 MicroStrategy / Strategy One Library，筛选包含大写字母的用户，并按执行人确认的编号将相关用户字段批量小写化。

该 Notebook 的目标是让执行过程可见、可控、可复核。执行人需要逐个 cell 运行，先查看候选清单，再输入编号确认实际处理范围，最后执行修改并复查结果。

## 2. 适用范围

适用于需要统一小写化 MSTR 用户字段的环境。

本 Notebook 会处理以下字段：

- 用户名显示字段：`display_name` / `full_name`
- 登录 ID：`username` / `account_login`
- 受信任验证请求用户 ID：`trust_id`

小写化规则：只改变字母大小写，数字和其他字符保持原样。例如 `UserABC123` 会变为 `userabc123`。

## 3. 文件说明

仓库关键文件如下：

- `mstr_user_lowercase_notebook.ipynb`：唯一执行入口，包含全部业务逻辑和交互步骤。
- `requirements.txt`：Python 依赖版本约束。
- `README.md`：项目快速说明。
- `docs/KT_MSTR_USER_LOWERCASE.md`：本文档。

当前版本不再需要单独的 `.py` 脚本。所有函数已经集成到 Notebook 中，便于交接团队直接打开、阅读、执行。

## 4. 环境要求

建议运行环境：

- Python 3.10、3.11、3.12 或 3.13
- Jupyter Notebook 或 JupyterLab
- 可访问目标 MSTR Library URL 的网络环境
- 具备修改用户信息权限的 MSTR 管理账号

依赖说明：

- `mstrio-py>=11.6.5.101,<12`
- `pandas>=2.0.0`

新版 `mstrio-py` 在 PyPI 上要求 Python `>=3.10,<3.14`。如果使用 Python 3.9，可能只能解析到较旧版本的 `mstrio-py`，并引发 pandas 版本冲突或安装解析时间过长。

## 5. 部署步骤

1. 克隆仓库：

```bash
git clone https://github.com/tony311536/mstr_user_lowercase_script.git
cd mstr_user_lowercase_script
```

2. 创建虚拟环境：

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

如果机器上没有 `python3.10`，请使用 `python3.11`、`python3.12` 或符合要求的 Python 版本。

3. 安装依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. 启动 Notebook：

```bash
jupyter notebook mstr_user_lowercase_notebook.ipynb
```

也可以使用 JupyterLab：

```bash
jupyter lab
```

然后在文件列表中打开 `mstr_user_lowercase_notebook.ipynb`。

## 6. 连接配置

Notebook 第 2 步会读取以下环境变量：

- `MSTR_LIBRARY_URL`
- `MSTR_USERNAME`
- `MSTR_PASSWORD`
- `MSTR_LOGIN_MODE`

建议用环境变量提供连接信息：

```bash
export MSTR_LIBRARY_URL="https://your-library.example.com/MicroStrategyLibrary/"
export MSTR_USERNAME="mstr"
export MSTR_PASSWORD="your-password"
export MSTR_LOGIN_MODE="1"
```

如果未设置 `MSTR_PASSWORD`，Notebook 会通过 `getpass()` 要求执行人输入密码，密码不会显示在 Notebook 输出中，也不会写入 Notebook 文件。

安全要求：

- 不要把真实密码写入 Notebook。
- 不要把真实密码提交到 Git。
- 如果密码曾经被贴到聊天、文档或日志中，应尽快轮换。

## 7. Notebook 执行步骤

### Step 1：导入依赖并定义工具函数

此 cell 会导入 pandas、mstrio，并定义后续会使用的函数。

成功标志：

- 输出 pandas 版本。
- 输出 `工具函数加载完成。`

常见错误：

- `ModuleNotFoundError: No module named 'mstrio'`：说明没有安装依赖，请执行 `pip install -r requirements.txt`。
- Python 版本过低：请切换到 Python 3.10 或更高版本。

### Step 2：配置并登录 MSTR Library

此 cell 会创建 `Connection`。

成功标志：

- 输出 `已连接: <library_url>`。

注意：

- 如果账号权限不足，后续修改用户时可能失败。
- 如果 Library URL 不可访问，会在此处或下一步获取用户时报错。

### Step 3：列出当前平台全部用户并导入 DataFrame

此 cell 会调用 `list_users(connection=connection)`，并显示当前平台用户清单。

检查点：

- 用户数量是否合理。
- 表格中是否包含 `display_name`、`login_id`、`account_login`、`trust_id`、`enabled`。

### Step 4：筛选包含大写字母的用户

此 cell 会筛选以下字段中包含大写字母的用户：

- `display_name`
- `full_name`
- `login_id`
- `account_login`
- `trust_id`

检查点：

- 如果数量为 0，说明没有需要处理的用户，可以停止执行。
- 如果数量很大，建议先抽查用户名是否符合预期。

### Step 5：选择本次要实际小写化的用户

此 cell 是主要交互步骤。

它会默认剔除疑似平台自带用户，然后为每个候选用户生成 `batch_no`。

执行人需要根据表格输入处理范围：

- 输入 `1`：只处理编号 1。
- 输入 `1;3;5`：处理编号 1、3、5。
- 输入 `all`：处理全部候选用户。

输入规则：

- 多个编号必须用英文分号 `;` 分隔。
- 不支持中文分号 `；`。
- 不支持逗号。
- 不支持不存在的编号。
- 如果输入错误，cell 会提示错误并要求重新输入。

输出结果：

- `本次确认要实际小写化的用户数量`
- 本次确认处理的用户表格

### Step 6：生成最终变更清单并检查冲突

此 cell 会显示旧值和新值：

- `display_name` -> `new_display_name`
- `login_id` -> `new_login_id`
- `trust_id` -> `new_trust_id`

同时会检查小写后的登录 ID 是否冲突。

如果发现冲突，Notebook 会停止执行，并显示冲突详情。此时不要执行 Step 7，需要先人工处理冲突。

### Step 7：实际执行小写化

此 cell 会真实修改 MSTR 用户。

执行前必须确认：

- Step 5 选择的编号正确。
- Step 6 的变更清单正确。
- Step 6 未发现登录 ID 冲突。

执行结果会输出 `result_df`，其中：

- `success=True` 表示该用户修改成功。
- `success=False` 表示该用户修改失败，错误原因在 `message` 字段中。

如果有任何失败项，Notebook 会抛出错误，执行人需要根据 `message` 处理。

### Step 8：再次列出当前平台用户并检查结果

此 cell 会重新拉取用户清单，并检查本批次目标用户是否仍包含大写字母。

成功标志：

- `本批次目标用户中仍包含大写字母的数量: 0`
- 输出 `检查成功：本批次目标用户已完成小写化。`
- 输出 `恭喜，批处理脚本运行成功！`

如果数量不为 0，需要查看输出表格确认哪些字段仍包含大写字母。

## 8. 运行前检查清单

执行前请确认：

- 已在正确的 MSTR 环境执行，而不是误连生产或测试环境。
- 使用的账号具备修改用户权限。
- 已确认要处理的是用户字段大小写问题，不是用户合并或账号迁移问题。
- 执行团队知道 Step 7 会真实修改用户。
- 已确认疑似平台自带用户默认剔除。
- 如需处理平台自带用户，必须先经过额外审批，并修改 Step 5 中的 `exclude_system_users`。

## 9. 执行后检查清单

执行后请确认：

- Step 7 中 `result_df["success"]` 全部为 `True`。
- Step 8 中本批次目标用户剩余大写数量为 0。
- 抽查 MSTR 管理界面中用户显示名、登录 ID、受信任验证请求用户 ID 是否符合预期。
- 将执行结果截图或导出保存到团队变更记录中。

## 10. 常见问题

### 10.1 `DataFrame` 没有 `applymap`

原因：pandas 2.x 中 `DataFrame.applymap()` 已被 `DataFrame.map()` 替代。

当前 Notebook 已使用兼容写法：优先使用 `DataFrame.map()`，旧 pandas 环境才 fallback 到 `applymap()`。

### 10.2 安装 `mstrio-py` 很慢或解析失败

优先检查 Python 版本。新版 `mstrio-py` 要求 Python `>=3.10,<3.14`。

如果使用 Python 3.9，pip 可能解析到老版本 `mstrio-py`，并触发 pandas 版本冲突或 notebook 依赖回溯。

### 10.3 输入编号后提示编号不存在

请确认输入的是 Step 5 表格里的 `batch_no`，不是 DataFrame 左侧索引，也不是用户 ID。

正确示例：

```text
1
1;3;5
all
```

错误示例：

```text
1,3,5
1；3；5
abc
999
```

### 10.4 Step 6 提示登录 ID 冲突

说明某个用户小写化后的登录 ID 与现有用户或本批次其他用户重复。

处理方式：

- 不要执行 Step 7。
- 人工确认冲突用户。
- 先在 MSTR 中处理重复账号或调整处理范围。
- 重新执行 Step 3 到 Step 6。

### 10.5 Step 7 部分用户修改失败

查看 `result_df` 中 `success=False` 的行，并读取 `message` 字段。

常见原因：

- 当前账号权限不足。
- 目标用户被系统保护。
- 用户字段被外部身份源同步管控。
- 登录 ID 冲突或违反平台规则。

## 11. 回滚思路

当前 Notebook 不自动执行回滚。因为用户登录 ID、认证 ID 等字段属于身份管理范畴，自动回滚可能造成新的冲突。

如果需要回滚：

1. 保留 Step 6 的变更清单截图或导出结果。
2. 根据 `display_name`、`login_id`、`trust_id` 的旧值，在 MSTR 管理界面或另一个受控脚本中恢复。
3. 回滚前同样需要检查登录 ID 冲突。

建议在正式执行前保存 Step 6 的预览表格作为变更记录。

## 12. 维护建议

- Notebook 中的 `SYSTEM_USER_NAMES` 用于识别疑似平台自带用户。如团队环境中有额外系统账号，可以补充到该集合中。
- 如果未来 `mstrio-py` 的 `User.alter()` 参数发生变化，需要优先检查 Step 7 中的 `user.alter(...)`。
- 如果团队希望保留每次执行记录，可以在 Step 7 后增加导出 `result_df.to_excel(...)` 或 `result_df.to_csv(...)`。
