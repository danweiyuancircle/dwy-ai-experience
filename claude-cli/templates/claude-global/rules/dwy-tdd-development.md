---
description: TDD 开发流程(新功能/bug 修复/重构的测试先行与回归策略)
category: 开发流程
---

# TDD 开发规则

所有代码变更必须遵循测试驱动开发流程。测试不是事后补的，是开发的起点。

## 开发流程

### 新功能

1. 先写测试 — 定义预期行为，测试此时应失败
2. 再写实现 — 用最简代码让测试通过
3. 重构优化 — 在测试保护下重构，确保始终通过

### Bug 修复

1. 先写复现测试 — 写一个能暴露 bug 的测试用例，确认它失败
2. 再修代码 — 修复 bug，确认测试通过
3. 跑回归 — 确认没有引入新问题

### 重构

1. 先跑现有测试 — 确认当前全部通过
2. 再重构 — 修改代码
3. 再跑测试 — 确认行为没变

## 回归测试

### 开发中：只跑受影响的测试

每次代码改动后，只运行受影响的测试文件，提高开发效率：

```bash
# 后端：只跑改动涉及的测试文件
uv run pytest tests/test_factor.py -v          # 改了 factor 相关代码
uv run pytest tests/test_tick.py tests/test_upload.py -v  # 改了多个模块

# 前端：只跑对应目录
pnpm vitest run tests/stores/               # 改了 store
pnpm vitest run tests/utils/format.test.ts   # 改了单个工具函数
```

判断"受影响的测试"的规则：
- 改了 `services/xxx.py` → 跑 `tests/test_xxx.py`
- 改了 `routers/xxx.py` → 跑 `tests/test_xxx.py`
- 改了 `schemas/` 或 `models/` → 跑引用了它们的测试
- 改了 `conftest.py` 或公共依赖 → 全量回归
- 不确定影响范围 → 全量回归

### 提交前：跑受影响的测试即可

提交前确保受影响的测试通过即可，不要求全量回归。全量测试留给 CI 或手动触发。

## TEST_CASES.md

每个包/项目维护一份 `TEST_CASES.md`，记录所有测试用例的清单：

- 人类可读，方便审查和手动编辑
- 新增/修改/删除功能时必须同步更新
- 内容与实际测试文件保持一致
- 作为版本回测基准

## 禁止事项

- **禁止**不写测试就提交功能代码
- **禁止**写完代码再补测试（先测试后代码）
- **禁止**测试不通过就提交
- **禁止** TEST_CASES.md 与实际测试不同步
