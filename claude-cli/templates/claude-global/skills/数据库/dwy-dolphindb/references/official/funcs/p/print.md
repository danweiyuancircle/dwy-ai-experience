---
source_url: https://docs.dolphindb.cn/zh/funcs/p/print.html
fetched_at: 2026-05-19T09:34:31Z
category: funcs
title: print
sha1: 46bff94d172c49c86109a027dcc3291cb23f7302
---

# print

## 语法

`print(X)`

## 详情

打印结果和变量的内容。

注：

DolphinDB `print` 与 Python 内置 [print](https://docs.python.org/3/library/functions.html#print) 的核心功能相同，区别在于 DolphinDB `print`
只接收一个 DolphinDB 对象，Python `print` 可接收多个对象，并支持通过
*sep*、*end*、*file* 和 *flush* 参数控制分隔符、行尾、输出位置和缓冲刷新。

## 参数

**X** 可以是任意数据。

## 返回值

无。

## 例子

```dolphindb
x=rand(10000,10);
print x;
// output: [9786,9501,8116,1266,1719,789,8162,3113,2740,6323]
```

字典的输出格式为“键->值”。键的输出顺序由创建字典时指定的的 *ordered*
参数决定。

```dolphindb
x=1 6 3
y=4.5 7.8 4.3
// 不指定 ordered 参数，默认为 false，表示无序字典
z=dict(x,y);
// 无序字典在输出时不保留输入顺序
print(z)
/* output:
3->4.3
6->7.8
1->4.5
*/

// 指定 ordered=true，表示有序字典
z1=dict(x,y,true)

// 有序字典在输出时会保留键值对的输入顺序
print(z1)
/* output:
1->4.5
6->7.8
3->4.3
*/
```
