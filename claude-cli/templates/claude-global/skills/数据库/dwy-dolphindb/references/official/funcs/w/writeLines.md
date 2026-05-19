---
source_url: https://docs.dolphindb.cn/zh/funcs/w/writeLines.html
fetched_at: 2026-05-19T09:44:10Z
category: funcs
title: writeLines
sha1: c012a68963ad59ec2d11c3a6988bd356925c65a2
---

# writeLines

## 语法

`writeLines(handle, object, [offset=0], [length],
[windowsLineEnding])`

## 详情

向句柄中写入给定的行数。

## 参数

**length** 是往句柄中写入的行数。

其他参数同 [writeLine](writeLine.html) 函数。

## 返回值

整型标量，表示成功写入的行数。

## 例子

```dolphindb
timer(10){
   x=rand(`IBM`MSFT`GOOG`YHOO`ORCL,10240)
   eachRight(writeLine, file("test.txt","w"),x)
   fin = file("test.txt")
   do{ y=fin.readLine() } while(!y.isVoid())
    fin.close()
};

// output
Time elapsed: 277.548 ms

timer(10){
   x=rand(`IBM`MSFT`GOOG`YHOO`ORCL,10240)
   file("test.txt","w").writeLines(x)
   fin = file("test.txt")
   do{ y=fin.readLines(1024) } while(y.size()==1024)
   fin.close()
};

// output
Time elapsed: 28.003 ms
```
