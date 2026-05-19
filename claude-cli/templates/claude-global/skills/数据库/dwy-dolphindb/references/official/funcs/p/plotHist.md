---
source_url: https://docs.dolphindb.cn/zh/funcs/p/plotHist.html
fetched_at: 2026-05-19T09:34:14Z
category: funcs
title: plotHist
sha1: 5ce5bded1e4c621febc0fbf82684301776d0dedd
---

# plotHist

## 语法

`plotHist(data, [binNum], [range], [title])`

## 详情

生成柱状图图表对象的系统函数。

## 参数

**data** 可以是向量，矩阵或表列。

**binNum** 是柱状图显示的柱数。

**range** 是表示柱状图的数据范围的数据对。

**title** 是图表的标题。

## 返回值

无。

## 例子

```dolphindb
x=norm(0.0, 1.0, 10000);
plotHist(x, 10)
```

  
![plothist1](../../images/plotHist01.png)  

```dolphindb
plotHist(x, 10, -2:2)
```

  
![plothist2](../../images/plotHist02.png)
