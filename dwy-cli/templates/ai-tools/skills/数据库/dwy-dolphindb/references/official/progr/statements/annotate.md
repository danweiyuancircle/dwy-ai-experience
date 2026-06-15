---
source_url: https://docs.dolphindb.cn/zh/progr/statements/annotate.html
fetched_at: 2026-05-19T09:01:46Z
category: progr
title: 注解
sha1: 7edc380bdc37bd04a00f161615dc2c3ff94dfd9a
---

# 注解

注解主要在单元测试中使用，在当前会话中生成数据对，用于打印输出一个测试用例的细节。

## 语法

```dolphindb
@<topic>:<sub_topic1>=<expr1>,
<sub_topic2>=<expr2>,
...
```

## 例子

```dolphindb
1:3+1;
ct = count(1..10)
assert ct == 11;
// output
Testing case testing count failed

@testing:case="function_and_ex", exception=1;

@testing_case;
// output
function_and_ex

@testing_exception;
// output
1
```
