---
source_url: https://docs.dolphindb.cn/zh/progr/closure.html
fetched_at: 2026-05-19T09:02:39Z
category: progr
title: 闭包
sha1: 321a79da2df9f24d7f56ef4756b05098ecf5f9ae
---

# 闭包

闭包是一个函数对象，它能保存该函数对象的作用域中的值，不论这个函数对象的作用域是否已经失效。

当lambda表达式被定义在另一个函数中时，它将自动得到父函数作用域的访问权。

```dolphindb
g=def(a){return def(b): a pow b};
g(10)(5);
// output
100000

def mixture(a,b){return def(c): c*(a-b)+(1-c)*(a+b)};
g=mixture(10,5);
g(0.1);
// output
14

def f(a,b){return def(x): a*x+b*(1-x)};
f(5,10)(0.2);
// output
9
```
