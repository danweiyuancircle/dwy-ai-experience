---
source_url: https://docs.dolphindb.cn/zh/progr/statements/doWhile.html
fetched_at: 2026-05-19T09:01:53Z
category: progr
title: do-while
sha1: fb780d927a2691098e6ec687350adbe0fa51e85d
---

# do-while

## 语法

```dolphindb
do{

[statements]

}

while (conditions);
```

## 详情

do-while循环首先执行do语句，然后检查循环体中的条件，保证循环体至少被执行一次。语句不能以"while"开头。do-while语句中都是必须使用圆括号()和花括号{}。

请注意，如果conditions是NULL或者!NULL，则按照false处理。

## 例子

```dolphindb
x=1
do {x+=2} while(x<100)
x;
// output
101

x=1
y=0
do {x+=y; y+=1} while(x<100 and y<10);
x;
// output
46
y;
// output
10
```
