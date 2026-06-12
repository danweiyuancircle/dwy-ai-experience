---
source_url: https://docs.dolphindb.cn/zh/pydoc/py.html
fetched_at: 2026-05-19T09:52:40Z
category: pydoc
title: Python API
sha1: b9595631a76291d78e617c7a3a947b7207170083
---

# Python API

**dolphindb** 是 DolphinDB 的官方 Python API，用于连接 DolphinDB 服务端和 Python
客户端，从而实现数据的双向传输和脚本的调用执行。dolphindb 可以方便您在 Python 环境中调用 DolphinDB
进行数据的处理、分析和建模等操作，利用其优秀的计算性能和强大的存储能力来帮助您加速数据的处理和分析。在下文中提到的 dolphindb 均指代 DolphinDB
API。

本手册共提供三大章节——快速开始，基本操作和进阶操作。

- 快速开始章节将介绍 dolphindb 的安装说明、简单示例和常用操作。
- 基本操作章节将介绍使用 dolphindb 的基本操作，如
  Session(会话)、DBConnectionPool（连接池）、追加数据、流订阅（基本）和异步写入的相关方法、注意事项和使用示例等。
- 进阶操作章节将详细说明类型转换、多种上传和写入数据方法、流订阅（进阶）、事件发送及订阅、面向对象操作数据库的方法，以及其他功能。

dolphindb 提供了多种接口函数，可用于连接服务器、执行脚本、发送消息等。此外，dolphindb 支持数据的批量处理和异步执行，以及多种数据类型的交互，如
pandas.DataFrame、arrow.Table 等。dolphindb 支持多种操作系统和 Python 版本（参见 [安装](QuickStart/Install.html#%E5%AE%89%E8%A3%85) ），方便用户使用。同时，它使用 Pybind11 编写 C++
库，从而优化后台多线程的处理，极大提高了数据交互的性能。

若您对本手册有任何宝贵意见，诚邀您通过  [DolphinDB 社区](https://ask.dolphindb.net)与我们进行反馈交流。
