# 数据源与参考资料

本 skill 的所有内容溯源。需要查更新 / 深入细节时直接进官方。

## 官方文档（中文）

| 资源 | URL | 用途 |
|---|---|---|
| 金融用户入门 | https://docs.dolphindb.cn/zh/tutorials/new_users_finance.html | 建库 / 导入 / SQL 批计算完整范式 |
| 使用须知 | https://docs.dolphindb.cn/zh/tutorials/usage_guidelines.html | 库表/SQL/语法/运维所有反模式 |
| 作业管理教程 | https://docs.dolphindb.cn/zh/tutorials/job_management_tutorial.html | getConsoleJobs / cancelJob 等命令 |
| 函数手册 | https://docs.dolphindb.cn/zh/funcs/ | 所有内置函数签名 |

## Python SDK（dolphindb 3.0.4）

主入口：https://docs.dolphindb.cn/zh/pydoc/

| 章节 | URL |
|---|---|
| Session 创建 | https://docs.dolphindb.cn/zh/pydoc/BasicOperations/Session/Constructor.html |
| Session connect | https://docs.dolphindb.cn/zh/pydoc/BasicOperations/Session/Connect.html |
| Session 常用方法 | https://docs.dolphindb.cn/zh/pydoc/BasicOperations/Session/OtherParams.html |
| 异步任务提交 | https://docs.dolphindb.cn/zh/pydoc/BasicOperations/AsyncWrites/SessionAsyncMode.html |
| 离线安装 | https://docs.dolphindb.cn/zh/tutorials/python_api_install_offline.html |
| Release Notes | https://docs.dolphindb.cn/zh/ReleaseNotes/api/python_rn.html |

## 英文版（部分中文还没翻译，英文更完整）

主入口：https://docs.dolphindb.com/en/pydoc/

## GitHub 仓库

| 仓库 | URL | 用途 |
|---|---|---|
| Python SDK 源码 | https://github.com/dolphindb/python-sdk | 看源码确认行为 |
| Python SDK README | https://github.com/dolphindb/api_python3/blob/master/README.md | 快速上手 |

## 版本基线

本 skill 验证于：
- DolphinDB Server：**3.0 社区版**
- Python SDK：**dolphindb==3.0.4**
- 集群拓扑：1 控制 + 2 数据节点
- 资源：2 核 / 8GB / 33TB

跨大版本（如 2.x → 3.x，或 3.x → 4.x）部分行为会变，遇到不符必须回官方文档核对。
