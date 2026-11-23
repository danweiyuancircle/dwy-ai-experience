---
source_url: https://docs.dolphindb.cn/zh/progr/statements/break.html
fetched_at: 2026-05-19T09:01:49Z
category: progr
title: break
sha1: 57ae120aef4e78eac1c1b826514a749ae43ebaf0
---

# break

## 详情

break 语句用于跳出一层循环。

## 例子

```dolphindb
def printloop(a,b){
   for(s in a:b){
       print "outer "+string(s)
       for(t in a:b){
           print "inner "+string(t)
           if (mod(t,10)==1){
                   break
           }
       }
   }
};

printloop(9,15);

// 当t=11时跳出循环内层循环，外层循环继续执行，共执行了6次
```
