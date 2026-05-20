# ✅ MSTR 用户批量小写化 Notebook KT 文档

本仓库提供一个交互式 Notebook，用于通过 `mstrio-py` 连接 MicroStrategy / Strategy One Library，筛选包含大写字母的用户，并由执行人输入编号确认后，实际将选中的用户字段批量小写化。

唯一执行入口：

- `mstr_user_lowercase_notebook.ipynb`

当前版本不再提供 `.py` 命令行脚本。全部业务逻辑已经集成到 Notebook 中，便于执行团队逐步查看、确认、执行和复核。

## 1. 处理范围

Notebook 会处理以下字段：

- `display_name` / `full_name`：用户显示名。
- `login_id`：账号登录 ID，也就是 account login。两者在当前使用场景下按同一登录字段展示，不再重复显示两列。
- `trust_id`：受信任验证请求用户 ID。

小写化规则：

- 只改变英文字母大小写。
- 数字保持不变。
- 其他字符保持不变。

示例：

```text
ZHANX562 -> zhanx562
UserABC123 -> userabc123
```

## 2. 环境要求

建议运行环境：

- Python 3.10、3.11、3.12 或 3.13
- Jupyter Notebook 或 JupyterLab
- 可以访问目标 MSTR Library URL 的网络环境
- 具备修改用户信息权限的 MSTR 管理账号

依赖文件：

```text
requirements.txt
```

已显式包含：

- `mstrio-py`
- `pandas`
- `ipython`
- `ipykernel`
- `notebook`

这样执行团队安装依赖后，通常不会再被额外提示安装 IPython kernel。

## 3. 部署步骤

克隆仓库：

```bash
git clone https://github.com/tony311536/mstr_user_lowercase_script.git
cd mstr_user_lowercase_script
```

创建虚拟环境：

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

如果机器上没有 `python3.10`，可以使用其他符合要求的 Python 版本，例如 `python3.11` 或 `python3.12`。

安装依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

启动 Notebook：

```bash
jupyter notebook mstr_user_lowercase_notebook.ipynb
```

也可以使用 JupyterLab：

```bash
jupyter lab
```

## 4. 连接配置

Notebook 会读取以下环境变量：

- `MSTR_LIBRARY_URL`
- `MSTR_USERNAME`
- `MSTR_PASSWORD`
- `MSTR_LOGIN_MODE`

推荐通过环境变量提供连接信息：

```bash
export MSTR_LIBRARY_URL="https://your-library.example.com/MicroStrategyLibrary/"
export MSTR_USERNAME="mstr"
export MSTR_PASSWORD="your-password"
export MSTR_LOGIN_MODE="1"
```

如果未设置 `MSTR_PASSWORD`，Notebook 会在运行登录 cell 时提示输入密码。

安全要求：

- ✅ 不要把真实密码写入 Notebook。
- ✅ 不要把真实密码提交到 Git。
- ✅ 如果密码曾出现在聊天、截图、日志或文档中，请尽快轮换。

## 5. Notebook 执行流程

### Step 1：✅ 导入依赖并加载工具函数

这个 cell 会导入依赖并定义所有工具函数。

特点：

- 代码较长，Notebook 中默认折叠。
- 正常只需要运行一次。
- 成功后会输出 `✅ 工具函数加载完成。`

如果报 `ModuleNotFoundError`，请确认已执行：

```bash
pip install -r requirements.txt
```

### Step 2：🔐 配置并登录 MSTR Library

此 cell 会创建 MSTR `Connection`。

成功标志：

```text
✅ 已连接: <library_url>
```

注意：

- 如果账号权限不足，后续实际修改时可能失败。
- 如果 Library URL 无法访问，会在登录或列用户时失败。

### Step 3：📋 列出当前平台全部用户

此 cell 用于确认连接环境和用户总量。

显示规则：

- 默认每页 20 条。
- 修改 `all_users_page` 可以翻页。
- 隐藏 DataFrame 默认索引，避免误认为业务编号。
- 只显示 `login_id`，不再重复显示 `account_login`。

### Step 4：🔎 筛选当前包含大写字母的用户

此 cell 会筛选当前仍包含大写字母的用户。

筛选字段：

- `display_name`
- `full_name`
- `login_id`
- `trust_id`

显示规则：

- 默认每页 20 条。
- 修改 `uppercase_users_page` 可以翻页。

如果数量为 0，说明当前没有需要小写化的用户，可以停止执行。

### Step 5：✅ 选择本次要实际小写化的用户

这是最关键的交互步骤。

Notebook 会：

1. 默认剔除疑似 MSTR 平台自带用户。
2. 给候选用户生成 `batch_no`。
3. 要求执行人输入要实际处理的编号。

输入示例：

```text
1
1;3;5
all
```

含义：

- `1`：只处理编号 1。
- `1;3;5`：处理编号 1、3、5。
- `all`：处理全部候选用户。

输入规则：

- 多个编号必须使用英文分号 `;`。
- 不支持中文分号 `；`。
- 不支持逗号。
- 不支持不存在的编号。
- 如果输入错误，Notebook 会显示 sample 并要求重新输入。

重要说明：

- 表格已隐藏 DataFrame 默认索引。
- 最前面的 `batch_no` 是唯一需要输入的编号。

### Step 6：🧾 生成最终变更清单并检查冲突

此 cell 不会修改 MSTR。

它会展示：

- `display_name` -> `new_display_name`
- `login_id` -> `new_login_id`
- `trust_id` -> `new_trust_id`

同时会检查小写后的 `login_id` 是否冲突。

如果发现冲突：

- 不要执行 Step 7。
- 先人工处理冲突用户。
- 重新从 Step 3 或 Step 4 开始检查。

### Step 7：🚀 实际执行小写化

此 cell 会真实修改 MSTR 用户。

执行前请确认：

- Step 5 选择的编号正确。
- Step 6 的变更清单正确。
- Step 6 未提示登录 ID 冲突。

执行结果字段：

- `success=True`：修改成功。
- `success=False`：修改失败，错误原因在 `message` 字段。

如果有任何失败项，Notebook 会抛出错误并停止。

### Step 8：✅ 复查当前全部大写用户

此 cell 不再列出全部平台用户，而是只列出当前仍包含大写字母的用户。

成功标准：

- 当前大写用户列表中不再包含 Step 5 选择的目标用户。

成功输出：

```text
✅ 检查成功：当前大写用户列表中已不再包含本批次目标用户。
🎉 恭喜，批处理脚本运行成功！
```

### Step 9：🔚 关闭 MSTR 连接

运行完成并复查成功后，请执行此 cell 显式释放 MSTR session。

Notebook 会按顺序尝试常见关闭方法：

- `connection.close()`
- `connection.logout()`
- `connection.disconnect()`

如果当前 `mstrio-py` 版本没有暴露这些方法，Notebook 会提示关闭 kernel，并依赖 MSTR 服务端 session timeout 自动清理。

## 6. 运行前检查清单

执行前请确认：

- ✅ 当前连接的是正确的 MSTR 环境。
- ✅ 使用账号具备修改用户权限。
- ✅ 已确认这是大小写规范化需求，不是账号合并或身份源迁移需求。
- ✅ 执行人知道 Step 7 会真实修改用户。
- ✅ 疑似平台自带用户默认剔除。
- ✅ 如需处理平台自带用户，必须经过额外审批，并修改 Notebook 中的 `exclude_system_users`。

## 7. 执行后检查清单

执行后请确认：

- ✅ Step 7 的 `success` 全部为 `True`。
- ✅ Step 8 当前大写用户列表中不再包含本批次目标用户。
- ✅ Step 9 已关闭 MSTR 连接，或已关闭 Notebook kernel。
- ✅ 可在 MSTR 管理界面抽查用户显示名、登录 ID、受信任验证请求用户 ID。
- ✅ 保存 Step 6 预览和 Step 7 结果，作为变更记录。

## 8. 常见问题

### `DataFrame` 没有 `applymap`

pandas 2.x 中 `DataFrame.applymap()` 已被 `DataFrame.map()` 替代。

当前 Notebook 已兼容：

- 新 pandas 优先使用 `DataFrame.map()`。
- 旧 pandas 自动 fallback 到 `DataFrame.applymap()`。

### 安装后仍提示 kernel

请确认使用的是安装依赖的同一个虚拟环境。

可执行：

```bash
python -m ipykernel install --user --name mstr-user-lowercase --display-name "MSTR User Lowercase"
```

然后在 Notebook 右上角选择 `MSTR User Lowercase` kernel。

### 输入编号后提示编号不存在

请确认输入的是 Step 5 表格里的 `batch_no`，不是用户 ID，也不是其他编号。

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

### Step 6 提示登录 ID 冲突

说明某个用户小写化后的 `login_id` 与现有用户或本批次其他用户重复。

处理方式：

- 不要执行 Step 7。
- 人工确认冲突用户。
- 调整账号或本次选择范围。
- 重新执行 Step 3 到 Step 6。

### Step 7 部分用户修改失败

查看结果表中的 `message` 字段。

常见原因：

- 当前账号权限不足。
- 目标用户受系统保护。
- 用户字段由外部身份源同步管控。
- 登录 ID 违反平台规则。

## 9. 回滚建议

Notebook 不自动执行回滚。

原因：

- 登录 ID 和受信任认证 ID 属于身份管理字段。
- 自动回滚可能遇到新的冲突。
- 回滚通常需要结合实际认证源和账号状态人工判断。

建议：

1. 正式执行前保存 Step 6 变更清单。
2. 执行后保存 Step 7 结果。
3. 如需回滚，基于 Step 6 的旧值人工恢复。
4. 回滚前同样检查登录 ID 冲突。

## 10. 维护建议

- `SYSTEM_USER_NAMES` 用于识别疑似平台自带用户。如团队环境有额外系统账号，可补充到该集合中。
- 如果未来 `mstrio-py` 的 `User.alter()` 参数变化，需要检查 Notebook Step 1 中的 `apply_changes()`。
- 如果希望长期留痕，可以在 Step 7 后增加 `result_df.to_excel(...)` 或 `result_df.to_csv(...)`。
