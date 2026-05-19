---
source_url: https://docs.dolphindb.cn/zh/progr/statements/continue.html
fetched_at: 2026-05-19T09:01:51Z
category: progr
title: continue
sha1: be05d2c94a5848f39f6fac92270d58e26deba648
---

# continue

## 详情

continue语句用于提前结束本次循环。

## 例子

```dolphindb
def printloop(a,b){
    for(s in a:b){
        if(mod(s,10)==1)
            continue
            print s
    }
}

printloop(10,13);
// output
10
12
// 当s=11时跳过该次循环
```
