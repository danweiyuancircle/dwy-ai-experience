---
source_url: https://docs.dolphindb.cn/zh/progr/data_mani/null_scalar.html
fetched_at: 2026-05-19T09:02:30Z
category: progr
title: 空值标量
sha1: 1f4dc5f4a9050745f586adf1075675e2d5713388
---

# 空值标量

```dolphindb
x=1.0+5.6*3+NULL+3;
x==NULL;
// output
1

typestr x;
// output
DOUBLE

x= x + `;
x==NULL;
// output
1

x=1
x==1<NULL;
// output
0

x==1 || NULL;
// output
1

NULL==NULL;
// output
1

!NULL==NULL;
// output
1
```
