---
name: dwy-redis
description: 设计、修改或排查 Redis 客户端、键、消息和部署配置时使用。
---

# Redis 开发

先核实实际 Redis 版本、客户端、拓扑与业务数据生命周期。按任务读 [Redis 规范](references/dwy-redis.md)，避免把团队特定客户端强加给已有项目；配置、凭据和外部输入按实际边界处理。涉及数据删除、迁移或生产设置时先核实影响与授权。
