# ✅ MSTR 用户批量小写化 Notebook KT 文档

本仓库提供一个交互式 Notebook，用于通过 `mstrio-py` 连接 MicroStrategy / Strategy One Library，筛选 **login_id 包含大写字母且 enabled** 的用户，并由执行人输入编号确认后，将选中的用户字段批量小写化。

唯一执行入口：

- `mstr_user_lowercase_notebook.ipynb`

## 1. 本次性能优化说明

旧流程在第 3 步会对每个用户对象读取 `full_name`、`trust_id`、`enabled` 等字段。对于 50 个用户问题不明显，但在六七千用户环境中，这类属性读取很可能触发逐用户详情请求，形成 N+1 API 调用，所以会非常慢。

新流程改为：

1. 第 3A 步只调用一次 `list_users(..., to_dictionary=True)` 获取轻量用户摘要。
2. 摘要阶段只保留 `login_id`，不读取 `enabled`、`full_name`、`trust_id` 等字段。
3. 第 4A 步先在本地筛选 `login_id` 含大写字母的用户。
4. 只对大写 login_id 候选用户逐个获取 `enabled/status` 和详情字段。
5. 再从大写候选用户中剔除 disabled 用户。
6. 翻页 cell 与数据获取 cell 分离，翻页不会重新请求 MSTR。

这样在大用户量环境下，主要请求量从“全部用户详情”降低为“全部 login_id 摘要 + 大写候选用户详情”。

## 2. 处理范围

Notebook 会处理以下字段：

- `display_name` / `full_name`：用户显示名。
- `login_id`：账号登录 ID，也就是 account login。
- `trust_id`：受信任验证请求用户 ID。

筛选范围：

- 第 3A 步只按 `login_id` 做全量轻量摘要。
- 第 4A 步先筛选 `login_id` 是否包含大写字母。
- 只对大写候选用户获取 enabled/status。
- disabled 用户不会进入最终候选处理范围。

小写化规则：

- 只改变英文字母大小写。
- 数字保持不变。
- 其他字符保持不变。

示例：

```text
ZHANX562 -> zhanx562
UserABC123 -> userabc123
```

## 3. 环境要求

建议运行环境：

- Python 3.10、3.11、3.12 或 3.13
- Jupyter Notebook 或 JupyterLab
- 可以访问目标 MSTR Library URL 的网络环境
- 具备修改用户信息权限的 MSTR 管理账号

安装依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` 已显式包含：

- `mstrio-py`
- `pandas`
- `ipython`
- `ipykernel`
- `notebook`

如果 Notebook 仍提示 kernel 不存在，可执行：

```bash
python -m ipykernel install --user --name mstr-user-lowercase --display-name "MSTR User Lowercase"
```

然后在 Notebook 右上角选择 `MSTR User Lowercase` kernel。

## 4. 部署步骤

```bash
git clone https://github.com/tony311536/mstr_user_lowercase_script.git
cd mstr_user_lowercase_script

python3.10 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

jupyter notebook mstr_user_lowercase_notebook.ipynb
```

也可以使用 JupyterLab：

```bash
jupyter lab
```

## 5. 连接配置

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

如果未设置 `MSTR_PASSWORD`，Notebook 会在登录 cell 中提示输入密码。

安全要求：

- ✅ 不要把真实密码写入 Notebook。
- ✅ 不要把真实密码提交到 Git。
- ✅ 如果密码曾出现在聊天、截图、日志或文档中，请尽快轮换。

## 6. Notebook 执行流程

### Step 1：✅ 导入依赖并加载工具函数

加载工具函数。长代码 cell 默认折叠。

成功输出：

```text
✅ 工具函数加载完成。
```

### Step 2：🔐 配置并登录 MSTR Library

创建 MSTR `Connection`。

成功输出：

```text
✅ 已连接: <library_url>
```

### Step 3A：⚡ 获取轻量用户摘要

只获取用户 login_id 摘要，不获取 enabled/status 或详情字段。

输出内容：

- 全部用户数量

### Step 3B：📋 分页查看用户摘要

只用于显示第 3A 步已经获取的数据。

修改 `summary_page` 可以翻页，不会重新请求 MSTR。

默认每页 20 条。

### Step 4A：🔎 先筛选大写 login_id，再按需获取 enabled 和详情

先在本地筛选：

- `login_id` 包含大写字母

然后只对这些大写候选用户获取：

- `enabled`
- `display_name`
- `full_name`
- `trust_id`

最后再剔除 disabled 用户。

如果候选数量为 0，可以停止后续执行。

### Step 4B：📋 分页查看大写候选用户详情

只用于显示第 4A 步已经获取的数据。

修改 `uppercase_details_page` 可以翻页，不会重新请求 MSTR。

### Step 5A：✅ 准备可选择清单

默认剔除疑似 MSTR 平台自带用户，并生成 `batch_no`。

如需处理平台自带用户，必须先经过额外审批，并修改 `exclude_system_users`。

### Step 5B：📋 分页查看可选择清单

只用于查看候选用户。

修改 `candidate_page` 可以翻页，不会重新筛选，也不会重新请求 MSTR。

注意：

- 表格隐藏了 DataFrame 默认索引。
- 最前面的 `batch_no` 是唯一需要输入的编号。

### Step 5C：🧑‍💻 输入本次实际处理编号

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

输入错误时，Notebook 会提示 sample 并要求重新输入。

### Step 6：🧾 生成最终变更清单并检查冲突

此步骤不会修改 MSTR。

它会展示：

- `display_name` -> `new_display_name`
- `login_id` -> `new_login_id`
- `trust_id` -> `new_trust_id`

同时会检查小写后的 `login_id` 是否与现有用户冲突。

如果发现冲突，不要执行 Step 7。

### Step 7：🚀 实际执行小写化

此步骤会真实修改 MSTR 用户。

执行前确认：

- Step 5C 选择的编号正确。
- Step 6 变更清单正确。
- Step 6 未提示冲突。

兼容性说明：

- Notebook 不传 `journal_comment` 参数，因为部分客户环境的 MSTR 版本会报 `Change journal comments require at least version 11.5.0900`。

### Step 8A：🔁 复查当前仍包含大写 login_id 的用户

重新获取轻量用户摘要，只检查当前仍包含大写字母的 `login_id`。

不会对全部用户获取详情。

成功标准：

- 本批次目标用户中仍包含大写 login_id 的数量为 0。

### Step 8B：📋 分页查看当前仍包含大写 login_id 的用户

只用于显示第 8A 步已经获取的数据。

修改 `uppercase_after_page` 可以翻页，不会重新请求 MSTR。

### Step 9：🔚 关闭 MSTR 连接

执行完成并复查成功后，请运行此步骤释放 MSTR session。

Notebook 会按顺序尝试：

- `connection.close()`
- `connection.logout()`
- `connection.disconnect()`

如果当前 `mstrio-py` 版本没有暴露这些方法，请关闭 Notebook kernel，并依赖 MSTR 服务端 session timeout 自动清理。

## 7. 运行前检查清单

- ✅ 当前连接的是正确的 MSTR 环境。
- ✅ 使用账号具备修改用户权限。
- ✅ 已确认这是大小写规范化需求，不是账号合并或身份源迁移需求。
- ✅ 执行人知道 Step 7 会真实修改用户。
- ✅ 已理解当前版本先筛选大写 login_id，再只对大写候选获取 enabled/status。

## 8. 执行后检查清单

- ✅ Step 7 的 `success` 全部为 `True`。
- ✅ Step 8A 中本批次目标用户仍包含大写 login_id 的数量为 0。
- ✅ Step 9 已关闭 MSTR 连接，或已关闭 Notebook kernel。
- ✅ 可在 MSTR 管理界面抽查用户显示名、登录 ID、受信任验证请求用户 ID。

## 9. 常见问题

### 为什么之前第 3 步会非常慢？

很可能是因为对几千个 `User` 对象逐个读取详情属性，导致大量 API 请求。

新版本第 3 步只拿轻量摘要，第 4 步只对候选用户拿详情，避免全量详情读取。

### 翻页为什么拆成单独 cell？

避免翻页时重新执行 API 请求。

需要翻页时，只修改对应显示 cell 的 page 变量并重新运行该显示 cell。

### disabled 用户会处理吗？

不会。

当前版本只处理 `enabled=True` 的用户。disabled 用户不会进入最终候选清单。

### 如果 Step 6 提示登录 ID 冲突怎么办？

不要执行 Step 7。

请先人工确认冲突用户，调整账号或本次选择范围，然后重新执行 Step 3A 到 Step 6。

## 10. 回滚建议

Notebook 不自动执行回滚。

建议正式执行前保存 Step 6 变更清单，执行后保存 Step 7 结果。如需回滚，基于 Step 6 的旧值人工恢复，并在回滚前再次检查登录 ID 冲突。
