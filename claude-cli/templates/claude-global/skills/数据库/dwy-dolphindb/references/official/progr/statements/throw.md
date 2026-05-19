---
source_url: https://docs.dolphindb.cn/zh/progr/statements/throw.html
fetched_at: 2026-05-19T09:02:03Z
category: progr
title: throw
sha1: fb1d10c17c11c2149e619a156753f5c3b6f900f5
---

# throw

throw用于抛出一个用户定义的异常

## 例子

```dolphindb
try {if (1%2 == 1) throw "it is an odd"} catch(ex){print ex};
// output
"USER" : "it is an odd"

ex;
// output
"USER" : "it is an odd"
```
