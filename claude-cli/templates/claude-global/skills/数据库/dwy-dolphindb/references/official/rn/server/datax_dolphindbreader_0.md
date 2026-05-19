---
source_url: https://docs.dolphindb.cn/zh/rn/server/datax_dolphindbreader_0.html
fetched_at: 2026-05-19T09:52:19Z
category: rn
title: DataX-dolphindbreader
sha1: 617d6ac7b7869213c151335f8bee924c91ce9e2e
---

# DataX-dolphindbreader

## 新功能

- 新增支持自动切分多任务。特别地，支持在配置 *querySql* 时自动切分多任务。（**1.30.22.3**）
- 新增支持数据类型 DECIMAL32、DECIMAL64、DECIMAL128。（**1.30.22.3**）
- 新增支持自定义配置项参数 querySql。（**1.30.22.2**）

## 功能优化

- 优化了内部实现逻辑。（**1.30.22.3**）

## 故障修复

- 字符串的长度超长的情况下导出数据报错。（**1.30.22.3**）
- 修复*channel* 参数配置问题。（**1.30.22.3**）
