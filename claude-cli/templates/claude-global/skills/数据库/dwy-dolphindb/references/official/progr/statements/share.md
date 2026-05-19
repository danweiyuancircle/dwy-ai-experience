---
source_url: https://docs.dolphindb.cn/zh/progr/statements/share.html
fetched_at: 2026-05-19T09:02:02Z
category: progr
title: share
sha1: 8414850823bb68a5a0ef3ed2125d439aa76505a0
---

# share

## 语法

`share <table> as <shared name>`

或

`share <engine> as <engine name>`

## 详情

- 第一种用法：节点内的会话共享

  将一个表共享到当前节点的所有会话中。包括表在内的局部对象在其他会话中是不可见的，需要通过共享才能在其他会话中可见。

  共享表名必须与所有其他会话中的普通表名不同。DolphinDB 服务器可以最多定义 65535 张共享表。
- 第二种用法：为引擎添加写入锁

  通过 share
  语句，可以为引擎添加写入锁，从而允许当前节点的所有会话并发地向引擎写入数据（要求引擎共享后的名称和引擎名称相同）。注意：在其它会话中，需要通过函数
  `getStreamEngine` 来获取引擎的句柄。

注：

- 不可以将同一个流数据表通过修改共享变量名称的方式共享2次及以上。
- `share` 语句不能在自定义函数内部使用。由于 DolphinDB 的解析机制，函数体内的
  `share` 语句会导致语法解析错误（详见 [S06002](../../error_codes/S06002.html)）。如需在自定义函数中共享表或引擎，请使用
  `share` 函数。

## 例子

- 第一种用法

  ```dolphindb
  t1= table(1 2 3 as id, 4 5 6 as value);
  share t1 as table1;

  // 共享通过 loadTable 加载的分布式表
  CREATE DATABASE "dfs://valuedb" PARTITIONED BY VALUE(2023.01.01..2023.12.31),engine="TSDB"
  CREATE TABLE "dfs://valuedb"."pt"(
      date DATE,
      time TIME,
      sym SYMBOL,
      price DOUBLE
  )
  PARTITIONED BY date,
  sortColumns=`time

  share loadTable("dfs://valuedb", "pt") as pt
  ```
- 第二种用法

  在一个会话中定义一个引擎，且通过 share 语句进行共享。

  ```dolphindb
  trades = streamTable(1:0, `time`sym`price, [TIMESTAMP, SYMBOL, DOUBLE])
  share table(100:0, `sym`time`factor1, [SYMBOL, TIMESTAMP, DOUBLE]) as outputTable
  engine = createReactiveStateEngine(name="test", metrics=[<time>, <mavg(price, 3)>], dummyTable=trades, outputTable=outputTable, keyColumn=`sym)
  //通过 share 语句，将引擎 test 共享后，便可以对引擎进行并发写入
  share engine as "test"
  ```

  当前节点所连接的任意一个会话中执行以下脚本：

  ```dolphindb
  //第一个自定义函数，向 engine 写入数据
  def write1(mutable engine) {
  	N = 10
  	for (i in 1..500) {
  		data = table(take(now(), N) as time, take(`A`B, N) as sym, rand(10.0, N) as price)
  		getStreamEngine(engine).append!(data)
  	}
  }
  //第二个自定义函数，向 engine 写入数据
  def write2(mutable engine) {
  	N = 10
  	for (i in 1..500) {
  		data = table(take(now(), N) as time, take(`C`D, N) as sym, rand(10.0, N) as price)
  		getStreamEngine(engine).append!(data)
  	}
  }
  //提交作业，使 write1 和 write2 同时向引擎写入数据
  submitJob("j1", "j1", write1, "test")
  submitJob("j2", "j2", write2, "test")
  ```

  查看输出表中数据行数为 10000，正好是 write1 和 write2 写入的数据量之和。

  ```dolphindb
  select count(*) from outputTable 
  //output
  10000
  ```

相关文档：[取消变量](../objs/undef_var.html), [undef](../../funcs/u/undef.html)
