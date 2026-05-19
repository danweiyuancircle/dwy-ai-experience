---
source_url: https://docs.dolphindb.cn/zh/tutorials/stream_processing_volatility_fitting.html
fetched_at: 2026-05-19T09:49:19Z
category: tutorials
title: DolphinDB 流计算在商品期货交易的应用：波动率计算与拟合
sha1: 4631277b96c535fedaeba657693e7fc4cce68815
---

# DolphinDB 流计算在商品期货交易的应用：波动率计算与拟合

在期货期权市场中，隐含波动率具有重要的意义，因为它有助于投资者和交易员更好地理解和管理风险，并为决策提供重要参考。高波动率通常意味着市场价格波动较大，风险较高。在高波动率时，投资者可能会减少仓位规模，以降低潜在的损失。相反，在低波动率时，他们可以考虑增加仓位规模以寻求更高的回报。通过计算和监测波动率可以帮助交易员选择合适的策略、采取适当的风险控制措施、预测未来的市场波动等等。同时希腊字母则量化了期权价格对市场因素变化的敏感性，确保交易者能够有效对冲风险并优化报价策略。

但是由于市场价格和收益率中存在许多噪音和波动，这些噪音可能导致计算出来的波动率不稳定，波动较大。而且市场波动性通常不是恒定的，而是随着时间和市场情况变化而变化；收益率分布经常出现偏斜等情况。进行波动率拟合，有助于改善波动率估计的准确性，使波动率曲线更好地适应市场的复杂性和非线性特征。

![](images/stream_processing_volatility_fitting/1.png)

本教程基于 DolphinDB 流数据处理框架，实时计算商品期权的隐含波动率和希腊字母，并每隔1分钟对波动率曲线进行拟合。

注意：本教程包含的所有代码兼容 DolphinDB 2.00.13，3.00.3 及以上版本。

## 1. 场景概述

在期货期权市场中，隐含波动率的实时计算通常以 ​​Black-Scholes（BS）模型​​为基础。BS
模型假设标的资产价格服从对数正态分布，通过无套利定价原理推导出欧式期权的理论价格，其核心公式通过标的资产价格、行权价、剩余期限、无风险利率和波动率五个变量计算期权价值。然而，BS
模型默认标的资产可无限分割且无分红，对期货期权适用性有限，其改进版本 ​​Black-76
模型​​——将标的资产价格替换为期货价格，并基于期货合约到期日与期权到期日的关系调整定价逻辑，更适用于大宗商品期货期权、利率期货期权等场景，尤其在标的资产存在持有成本或便利收益率时精度显著提升。公式如下：

![](images/stream_processing_volatility_fitting/2.png)

图 1. 图1-1 看涨期权（Call Option）定价公式

![](images/stream_processing_volatility_fitting/3.png)

图 2. 图1-2 看跌期权（Put Option）定价公式

![](images/stream_processing_volatility_fitting/4.png)

图 3. 图1-3 公式参数

其中：

- **F**：标的期货的当前价格
- **K**：期权执行价
- **T**：到期时间（年化）
- **r**：无风险利率（连续复利）
- **σ**：期货价格年化波动率
- **N(…)**：标准正态分布累积函数

本文将基于 Black-76 模型计算隐含波动率。 基于 Black-76
模型计算隐含波动率的常用算法有牛顿迭代法（Newton-Raphson）、二分法（Bisection）​、布伦特法（Brent's
Method）等。相比于其他两种算法，布伦特法（Brent's Method）结合二分法和逆二次插值的混合优化算法，兼具稳定性和快速收敛特性，DolphinDB
也开发了对应的函数方便用户使用，详见[brentq](../funcs/b/brentq.html)。
其他算法的实现与应用可以参考教程[利用JIT加速计算 ETF 期权隐含波动率和希腊值](IV_Greeks_Calculation_for_ETF_Options_Using_JIT.html)。

## 2. 实现思路

本章节将介绍下 DolphinDB 如何基于流计算引擎，实现实时隐含波动率计算、希腊字母计算、波动率微笑曲线构建与平滑。实现架构图如下：

![](images/stream_processing_volatility_fitting/5.png)

图 4. 图2-1 流程图

针对实盘环境，DolphinDB 提供 CTP 插件接入 tick 行情：[DolphinDB CTP 行情插件最佳实践指南](../plugins/ctp_best_practice.html)

针对研究环境，DolphinDB 提供`replay`历史数据回放函数，模拟实时行情：[数据回放](data_replay.html)

行情接入后，主要经过以下几个步骤：

1. 数据有效性筛选：本教程中只是对实时行情数据进行了一些简单的筛选，如：买卖价格，交易量都要大于0、数据时间在市场交易时间内、接到数据的时间与实际交易的数据时间差不应该超过5秒等。用户可以根据自己的需要增加筛选规则。筛选的同时会使用基本信息表补齐一些必要信息。筛选之后，会分别将期货行情、期权行情保存到不同的流数据表中。
2. 期货价格选取：在计算期权隐含波动率的时候，需要确定期货价格。本教程选定的方式为，根据期权行情的数据时间去查找离该时间最近的一个期货价格的数据。这里用到了
   DolphinDB 独有的[asof join
   引擎](../stream/asof_join_engine.html)，按时间邻近度关联期货期权行情表，最后将期权价格、最近的期货价格、期货期权基本信息等合并到一个流表中。
3. 隐含波动率与希腊字母计算：前面的章节已经介绍了我们使用的模型与算法。这里我们用到了[响应式状态引擎](../stream/reactive_state_engine.html)对每一条有效行情单独计算隐含波动率和希腊字母值。
4. 波动率微笑曲线构建与平滑：

   1. 一般隐含波动率曲线都用流动性较好的虚值期权来构建，示例中将每隔1分钟构建一次实时波动率曲线。考虑到部分合约交易量较小，并不是所有时刻都有行情数据，所以本教程使用[横截面引擎](../stream/cross_sectional_engine.html)而非[时序聚合引擎](../stream/time_series_engine.html)，每次使用每个期权合约执行价最新的隐含波动率来构建曲线。
   2. 曲线平滑：由于一些波动率的缺失或者市场噪音或者波动导致构建的波动率曲线会比较粗糙。本教程使用常见的三次样条插值方案对曲线进行平滑处理。同样，DolphinDB
      提供了开箱即用的函数[cubicSpline](../funcs/c/cubicspline.html)，除此之外，DolphinDB 还提供了[linearInterpolateFit](../funcs/l/linearinterpolatefit.html)、[pchipInterpolateFit](../funcs/p/pchipInterpolateFit.html)、[nss](../funcs/n/nss.html)等多种插值和拟合函数，用户可以按需使用合适的函数对曲线进行平滑处理。

## 3. 数据说明

本教程期货期权行情数据使用的是 CTP 实时数据。综合交易平台（Comprehensive Transaction Platform）简称
CTP，是服务于期货市场的业务管理系统。DolphinDB 提供了对接 CTP 系统的 CTP 插件，可以订阅期货市场的实时行情数据、查询商品信息。关于 CTP
插件的相关信息，可以参考教程：[DolphinDB CTP
行情插件最佳实践指南](../plugins/ctp_best_practice.html)CTP 实时行情数据表结构如下：

| **字段名称** | **数据类型** | **数据说明** |
| --- | --- | --- |
| TradingDay | DATE | 交易日期 |
| …… | …… | …… |
| UpdateTime | SECOND | 交易时间-秒 |
| UpdateMillisec | INT | 交易时间-微妙 |
| BidPrice1 | DOUBLE | 买入价格 |
| BidVolume1 | INT |  |
| AskPrice1 | DOUBLE | 卖出价格 |
| …… | …… | …… |
| InstrumentID | STRING | 期权或期货代码 |
| …… | …… | …… |

除了原始行情数据，本教程还使用了来自 CTP 系统的期货和期权基本信息数据，并对其进行了简单处理。表结构如下：

|  |  |  |
| --- | --- | --- |
| **字段名称** | **数据类型** | **数据说明** |
| ExchangeID | SYMBOL | 市场代码 |
| InstrumentName | STRING | 合约名称 |
| ……. | …… | …… |
| CreateDate | DATE | 创建日 |
| OpenDate | DATE | 上市日 |
| ExpireDate | DATE | 到期日 |
| …… | ……. | …… |
| StrikePrice | DOUBLE | 执行价 |
| OptionsType | SYMBOL | 期权类型 |
| UnderlyingMultiple | DOUBLE | 合约基础商品乘数 |
| CombinationType | SYMBOL | 组合类型 |
| InstrumentID | SYMBOL | 合约代码 |
| ExchangeInstID | SYMBOL | 合约在交易所的代码 |
| ProductID | SYMBOL | 产品代码 |
| UnderlyingInstrID | SYMBOL | 基础商品代码 |
| insertTime | TIMESTAMP | 更新时间 |
| prdCode | SYMBOL | 标的代码 |

## 4. 业务实现

在本教程最后的附录中，提供了样例数据和建库建表、导入数据的脚本。执行完建库建表脚本之后，可以执行以下脚本导入测试数据：

```dolphindb
YourDir = ""
// csv 导入基础信息
schemaInfo = select name,typeString from loadTable("dfs://option_info", "data").schema().colDefs
t = loadText(filename=YourDir+"option_info.csv", schema=schemaInfo)
tableInsert(loadTable("dfs://option_info", "data"), t)
// csv 导入期货期权行情数据
schemaMarket = select name,typeString from loadTable("dfs://ctp", "market").schema().colDefs
loadTextEx(dbHandle=database("dfs://ctp"), tableName="market", partitionColumns=["TradingDay","InstrumentID"], filename=YourDir+"market.csv", schema=schemaMarket)
```

导入成功后，依次执行附录中的《初始化环境.dos》、《函数与引擎定义.dos》、《数据回放.dos》代码，即可快速体验实时隐含波动率计算与曲线构建。

### 4.1 期货价格选取

如前文所述，DolphinDB 提供时间邻近度关联左右表引擎，可以直接通过创建引擎的方式实现根据期权报价时间找最近的期货价格，如下所示：

```dolphindb
ajEngine = createAsofJoinEngine(
  name="asofJoin",
  leftTable=ctpOptions,
  rightTable=ctpFutures,
  outputTable=futOptCrt,
  metrics=<[ctpOptions.InstrumentID, ctpFutures.assetCode, (ctpFutures.BidPrice1+ctpFutures.AskPrice1)\2, (ctpOptions.BidPrice1+ctpOptions.AskPrice1)\2, KPrice, CPMode, endDate]>,
  matchingColumn=[[`futureCode],[`InstrumentID]],
  timeColumn=`TradingTime,
  useSystemTime=false)
// subscribe topic
subscribeTable(tableName="ctpOptions", actionName="appendLeftStream", handler=getLeftStream(ajEngine), msgAsTable=true, offset=-1, hash=0)
subscribeTable(tableName="ctpFutures", actionName="appendRightStream", handler=getRightStream(ajEngine), msgAsTable=true, offset=-1, hash=1)
```

其中，期权行情为左表，期货行情为右表。对于每一笔期权行情数据，会从期货行情中获取临近的最新期货行情数据，并输出。读者可以通过参数*delayedTime*设置超时强制触发规则，详情请见引擎详细说明[asof join 引擎](../stream/asof_join_engine.html)。

### 4.2 波动率计算

`brent` 函数要求提供一个函数参数*f*，在一个给定区间 *[a, b]* 内求出函数 f(x)
的一个根*x0*，使得 f(x0)=0 ，所以在代码中除了实现 Black-76 的模型外，还定义了一个函数
`loss_function`，返回 Black-76 模型的定价与实际行情价格的差值，然后使用
`brent` 函数进行求解。计算代码如下：

```dolphindb
/* 
 * @Brief: 计算隐波，black_76 公式
 * @Param: F: 现货价格
 * @Param: K: 执行价
 * @Param: T: 剩余期限
 * @Param: r: 无风险利率
 * @Param: sigma: 波动率
 * @Param: option_type: 期权类型，1或-1，代表'C' or 'P'
*/
def black_76(F, K, T, r, sigma, option_type){
    d1 = (log(F \ K) + (0.5 * pow(sigma , 2) ) * T) \ (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if (option_type == 1){
        return exp(-r * T) * (F * cdfNormal(0,1,d1) - K * cdfNormal(0,1,d2))
    }else if( option_type == -1){
        return exp(-r * T) * (K * cdfNormal(0,1,-d2) - F * cdfNormal(0,1,-d1))
    }else{
        return ("Option type must be 1 or -1.")
    }
}
/* 
 * @Brief: 计算隐波，Brentq 的求解函数
 * @Param: sigma: 波动率
 * @Param: F: 现货价格
 * @Param: K: 执行价
 * @Param: T: 剩余期限
 * @Param: r: 无风险利率
 * @Param: option_type: 期权类型，1或-1，代表'C' or 'P'
 * @Param: market_price: 期权价格
*/
def loss_function(sigma, F, K, T, r, option_type, market_price){
    return black_76(F, K, T, r, sigma, option_type) - market_price
}
/**
 * @Brief: 计算隐波，Brentq 的求解函数
 * @Param: F: 现货价格
 * @Param: K: 执行价
 * @Param: T: 剩余期限
 * @Param: r: 无风险利率
 * @Param: option_type: 期权类型 ，1或-1，代表'C' or 'P'
 * @Param: market_price: 期权价格
 * @Return: 
 * @Sample usage:
 */
def implied_volatility_Black76Brentq(F, K, T, r, option_type, market_price){
	iv = double(NULL)
	try{ 
			iv = brentq(f=loss_function, a=1e-6, b=2, xtol=2e-12, rtol=1e-9, maxIter=100, funcDataParam=[F, K, T, r, option_type, market_price])[1]
	}catch(ex){
			writeLog("calculate error: " + ex)
	}
	return iv
}
```

### 4.3 波动率曲线构建与平滑

DolphinDB
的横截面引擎保存了所有分组的最新记录，有效解决部分合约因低频交易而缺少行情数据的问题。同时横截面引擎可以使用数据时间按照固定时间间隔触发。这里我们创建横截面引擎每隔数据时间1分钟，进行一次曲线构建与平滑。代码如下：

```dolphindb
crossEngine = createCrossSectionalEngine(
  name="crossEngine",
  metrics=<[last(assetCode), buildIVCurve(trigger, futureCode, assetCode, futurePrice, KPrice, CPMode, iv)]>,
  dummyTable=ivResult,
  outputTable=ivCurve,
  keyColumn=`futureCode`KPrice`CPMode,
  triggeringPattern='dataInterval',
  triggeringInterval=60*1000,
  timeColumn=`trigger,
  useSystemTime=false,
  contextByColumn=`futureCode,
  outputElapsedMicroseconds=true)
filterFn = def (msg) { // 过滤掉 iv 无效的数据
	return (select * from msg where iv > 0)
}
subscribeTable(tableName="ivResult", actionName="buildCurve", offset=-1, handler=append!{crossEngine}, msgAsTable=true, batchSize=10000, throttle=1, hash=3, filter=filterFn);
```

通常我们使用流动性较好的虚值期权来构建波动率曲线。使用每分钟最新的期货价格来作为基准查找看涨看跌的虚值期权，代码如下：

```dolphindb
strikePrices = KPrice[KPrice< lastPrice and CPMode == -1].join(KPrice[KPrice>= lastPrice and CPMode == 1])
stikeIvs = iv[KPrice< lastPrice and CPMode == -1].join(iv[KPrice>= lastPrice and CPMode == 1])
indexs = isort(strikePrices) // 排序
strikePrices = strikePrices[indexs]
stikeIvs = stikeIvs[indexs]
```

本文使用三次样条插值，先根据选取的所有虚值期权和隐含波动率构建模型，然后将中间的执行价格等分为50份，使用模型对这些价格进行插值，最终将原始的执行价及隐含波动率、平滑的执行价格及插值的隐含波动率，以
arrayVector 保存，代码如下：

```dolphindb
n = 50 // 样本数量
if(strikePrices.size() >= 3 ){ // 波动率数据太少，就不做拟合
  // 构建微笑曲线执行价坐标
  curvePrices = linspace(min(strikePrices), max(strikePrices), n, true)[1]$int
  // 构建三次样条插值模型
  cs = cubicSpline(strikePrices, stikeIvs)
  // 插值获得微笑曲线的波动率数据
  curveIvs = cubicSplinePredict(cs, curvePrices)
  // 返回插值结果
  tableInsert(objByName(`interResult), ( max(trigger), first(futureCode), first(assetCode), arrayVector([strikePrices.size()], strikePrices), arrayVector([stikeIvs.size()], stikeIvs), arrayVector([curvePrices.size()], curvePrices), arrayVector([curveIvs.size()], curveIvs) ))
}else{
  prices, ivs = NULL, NULL
  if(strikePrices.count()>0) prices, ivs = arrayVector([strikePrices.size()], strikePrices), arrayVector([stikeIvs.size()], stikeIvs)
  tableInsert(objByName(`interResult), ( max(trigger), first(futureCode), first(assetCode), prices, ivs, NULL, NULL ))
}
```

## 5. 结果展示

DolphinDB 提供可视化看板 Dashboard ，通过 Dashbord 可以构建实时波动率曲线并定时刷新，展示结果如下图：

![](images/stream_processing_volatility_fitting/6.png)

图 5. 图5-1 面板展示图

## 6. 总结

本文系统介绍了如何基于 DolphinDB 流数据处理框架，实时计算商品期权的隐含波动率和希腊字母，并对波动率曲线进行拟合和平滑。教程详细讲解了如何利用
DolphinDB 的流计算引擎，结合 Black-76 模型和 Brent
法等数值算法，实时计算隐含波动率和希腊字母。通过时间邻近度关联、横截面引擎等机制，实现了期货价格选取、实时行情数据筛选、波动率曲线的动态构建与三次样条插值平滑。最后，通过
DolphinDB Dashboard 实时展示波动率曲线信息。

## 7. 附件

建库建表脚本：[建库建表.dos](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/%E5%BB%BA%E5%BA%93%E5%BB%BA%E8%A1%A8.dos)

教程使用数据：[data.zip](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/data.zip)

数据导入脚本：[csv导入数据.dos](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/csv%E5%AF%BC%E5%85%A5%E6%95%B0%E6%8D%AE.dos)

环境初始化脚本：[1.初始化环境.dos](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/1.%E5%88%9D%E5%A7%8B%E5%8C%96%E7%8E%AF%E5%A2%83.dos)

流引擎与函数定义：[2.函数与引擎定义.dos](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/2.%E5%87%BD%E6%95%B0%E4%B8%8E%E5%BC%95%E6%93%8E%E5%AE%9A%E4%B9%89.dos)

数据回放脚本：[3.数据回放.dos](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/3.%E6%95%B0%E6%8D%AE%E5%9B%9E%E6%94%BE.dos)

DashBoard 展示模板：[dashboard.json](https://cdn.dolphindb.cn/downloads/tutorials/script/stream_processing_volatility_fitting/dashboard.json)
