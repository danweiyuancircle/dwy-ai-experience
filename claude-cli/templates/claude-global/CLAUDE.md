所有回答必须使用中文。

## 输出完整性要求

- **文件路径**：必须输出完整的绝对路径（如 `/Users/chances/WebstormProjects/dwy-shared/frontend/eui/src/components/input/EInput.vue`），禁止省略为相对路径或只写文件名
- **服务地址**：必须输出完整的 URL（如 `http://localhost:8000/api/users`），禁止省略协议、端口或路径
- **数据库连接串**：必须输出完整连接字符串（如 `postgresql+asyncpg://user:pass@localhost:5432/mydb`），禁止只写主机名或库名

## Agent 团队执行

所有任务默认启用 agent team 模式执行：任务可拆分时优先并行派遣 Agent，具体派遣策略、并行度、worktree 隔离、review 闭环等由 Claude 自行判断，不在此处硬编码规则。
