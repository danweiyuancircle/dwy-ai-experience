---
source_url: https://docs.dolphindb.cn/zh/db_distr_comp/cfg/para_cfg.html
fetched_at: 2026-05-19T09:00:13Z
category: db_distr_comp
title: 参数配置
sha1: 1447aff068fac0267364014ba989a072b6fc69a9
---

# 参数配置

DolphinDB 提供了一系列配置参数，方便用户根据实际情况进行合理的配置，以充分利用机器的硬件资源。

用户可通过 [getConfig](../../funcs/g/getConfig.html)
函数，查看配置项的值。

注：

大部分参数数据节点和计算节点均可配置。由于计算节点不存储数据，因此无需配置磁盘相关的参数。
