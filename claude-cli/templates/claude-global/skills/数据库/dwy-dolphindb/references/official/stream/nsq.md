---
source_url: https://docs.dolphindb.cn/zh/stream/nsq.html
fetched_at: 2026-05-19T09:05:41Z
category: stream
title: 行情数据插件：NSQ
sha1: 6a538f001a9609be755a4880b14569a80518b4d3
---

# 行情数据插件：NSQ

为对接恒生 NSQ 极速行情服务软件，DolphinDB 开发了 NSQ 插件。通过该插件能够获取上海和深圳市场的行情。主要获得以下三种行情：

1. 主推-现货深度行情主推回调（OnRtnSecuDepthMarketData->snapshot）
2. 主推-现货逐笔成交行情主推回调（OnRtnSecuTransactionTradeData->trade）
3. 主推-现货逐笔委托行情主推回调（OnRtnSecuTransactionEntrustData->orders）

恒生公司发布了 NSQ 极速行情服务软件的 SDK，名称为 HSNsqApi。其对应 linux 下的 libHSNsqApi.so 或 windows 下的
HSNsqApi.dll。编译时需要将对应动态库拷贝至插件项目的 lib/linux.x/win（如 lib/linux.x64)
文件夹。在运行时需要保证对应链接库能被找到。

请注意，DolphinDB 仅提供对接 HSNsqApi 的 NSQ 插件。数据源和接入服务可咨询数据服务商或证券公司。

NSQ 插件目前支持版本：[relsease200](https://gitee.com/link?target=https%3A%2F%2Fgithub.com%2Fdolphindb%2FDolphinDBPlugin%2Fblob%2Frelease200%2Fnsq%2FREADME.md), [release130](https://gitee.com/link?target=https%3A%2F%2Fgithub.com%2Fdolphindb%2FDolphinDBPlugin%2Fblob%2Frelease130%2Fnsq%2FREADME.md)。
