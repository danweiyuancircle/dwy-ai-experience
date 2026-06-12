---
source_url: https://docs.dolphindb.cn/zh/tutorials/pricing_functions.html
fetched_at: 2026-05-19T09:51:19Z
category: tutorials
title: FICC 与 Equity 定价函数
sha1: 00ab08bc68c7fe2360729ae71268664a4f95eec7
---

# FICC 与 Equity 定价函数

## 1. 前言

金融产品的定价是金融工程的语言和核心。​
**​准确的定价是市场有效运行、风险有效管理和产品持续创新的基石​**
​。理解定价的原理、重要性及其挑战，对于洞察金融市场、做出明智决策以及推动金融领域的健康发展都至关重要。

在无套利原则下，所有金融产品的定价公式为

![](image/pricing_functions/1.PNG)
其中：

- npv 为净现值(Net Present Value)
- cf\_i 为第 i 笔现金流(Cash Flow)，E 为风险中性测度下的期望函数
- df\_i 为第 i 期的折现因子(Discount Factor)

## 2. 基础定价接口

DolphinDB 提供基础定价函数接口设计，形式如下：

```dolphindb
xxxPricer(instrument, pricingDate, mktData, [setting], [model], [method])
```

其中 xxxPricer 为占位符，实际函数名根据金融产品类型不同而变化，例如 bondPricer、irFixedFloatingSwapPricer、fxEuropeanOptionPricer 等。

参数：

- instrument：INSTRUMENT 类型标量或向量，表示需要定价的金融产品，各种金融产品的定义可参考
  [parseInstrument](../funcs/p/parseInstrument.html)
- pricingDate：DATE类型，表示定价日期
- mktData：市场数据，根据不同产品的定价需要填入 Spot/Curve/Surface 等信息
- setting：可选参数，字典类型，主要是风险计量设定
- model：可选参数，字典类型，表示定价模型及模型的参数设定（主要针对期权产品）
- method： 可选参数，字典类型，表示定价方法（Analytic/PDE/MonteCarlo）及方法的参数设定（主要针对期权产品）

**返回值：**
NPV， CashFlow (可选)， Greeks (可选)

DolphinDB V3.00.5 提供的基础定价函数汇总如下：

| **资产类别** | **函数名** | **描述** |
| --- | --- | --- |
| 债券 | [bondPricer](../funcs/b/bondPricer.html) | 债券定价（贴现债/零息债/固定利率债） |
| 债券 | [bondFuturesPricer](../funcs/b/bondFuturesPricer.html) | 国债期货定价 |
| 利率 | [irDepositPricer](../funcs/i/irDepositPricer.html) | 存款定价 |
| 利率 | [irFixedFloatingSwapPricer](../funcs/i/irFixedFloatingSwapPricer.html) | 标准利率互换定价 |
| 外汇 | [fxForwardPricer](../funcs/f/fxForwardPricer.html) | 外汇远期定价 |
| 外汇 | [fxSwapPricer](../funcs/f/fxSwapPricer.html) | 外汇掉期定价 |
| 外汇 | [fxEuropeanOptionPricer](../funcs/f/fxEuropeanOptionPricer.html) | 外汇欧式期权定价 |
| 商品 | [cmFutEuropeanOptionPricer](../funcs/c/cmfuteuropeanoptionpricer.html) | 商品期货欧式期权定价 |
| 商品 | [cmFutAmericanOptionPricer](../funcs/c/cmfutamericanoptionpricer.html) | 商品期货美式期权定价 |
| 权益 | [eqEuropeanOptionPricer](../funcs/e/eqeuropeanoptionpricer.html) | 权益类欧式期权定价 |
| 权益 | [eqAmericanOptionPricer](../funcs/e/eqamericanoptionpricer.html) | 权益类美式期权定价 |

### 2.1 债券定价

债券是 FICC 业务中最大的交易品种。债券定价（
[bondPricer](../funcs/b/bondPricer.html)
）采用现金流折现模型，目前仅支持贴现债/零息债/固定利率债的定价。债券定价需要根据债券的类型，选择相应的折现曲线。这些曲线既可以用
[bondYieldCurveBuilder](../funcs/b/bondYieldCurveBuilder.html)
函数自己构建，也可以直接使用第三方即期曲线。下面分别给出一个例子。

**例 1： 贴现债定价**
( 259916.IB，
[259916\_25贴现国债16\_2025年记账式贴现(十六期)国债\_中国货币网](https://www.chinamoney.com.cn/chinese/zqjc/?bondDefinedCode=fbbjd59916)
)

```dolphindb
//step1: 生成instrument
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "DiscountBond",
    "instrumentId": "259916.IB",
    "start": 2025.03.13,
    "maturity": 2025.09.11,
    "issuePrice": 99.207,
    "dayCountConvention": "ActualActualISDA"
}
instrument = parseInstrument(bond)
//step2: 准备定价需要用到的曲线
/*
 因为该债券为国债，所以discoutCurve选取国债收益率曲线（即期）
 数据来源https://www.chinamoney.com.cn/chinese/bkcurvclosedyhis/index.html
*/ 
curve =  {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_TREASURY_BOND",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Compounded",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates":[2025.09.18, 2025.11.18, 2026.02.18, 2026.08.18, 2027.08.18, 2028.08.18, 2030.08.18,
             2032.08.18, 2035.08.18, 2040.08.18, 2045.08.18, 2055.08.18,2065.08.18, 2075.08.18],
    "values":[1.3000, 1.3700, 1.3898, 1.3865, 1.4299, 1.4471, 1.6401,
              1.7654, 1.7966, 1.9930, 2.1834, 2.1397, 2.1987, 2.2225] / 100.0
}
discountCurve = parseMktData(curve)
//step3: 调用定价函数
pricingDate = 2025.08.18
npv = bondPricer(instrument, pricingDate, discountCurve)
//step4: 打印结果
print(npv)
/* output:
99.914593552908201   
*/
```

**例2： 零息债定价**
( 250401.IB，
[250401\_25农发01\_中国农业发展银行2025年第一期金融债券\_中国货币网](https://www.chinamoney.com.cn/chinese/zqjc/?bondDefinedCode=eehegoxhfb)
)

```dolphindb
//step1: 生成instrument
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "ZeroCouponBond",
    "instrumentId": "250401.IB",
    "start": 2025.01.09,
    "maturity": 2026.02.05,
    "coupon": 0.0119,
    "dayCountConvention": "ActualActualISDA"
}
instrument = parseInstrument(bond)
//step2: 准备定价需要用到的曲线
/*
  因为该债券为农发债，所以discoutCurve选取农发债收益率曲线（即期）
  数据来源https://www.chinamoney.com.cn/chinese/bkcurvclosedyhis/index.html
*/
curve =  {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_ADBC_BOND",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Compounded",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    // 0.083 0.25 0.5 1.0 2.0 3.0 5.0 7.0 10.0 15.0 20.0
    "dates":[2025.09.18, 2025.11.18, 2026.02.18, 2026.08.18, 2027.08.18, 2028.08.18,
             2030.08.18, 2032.08.18, 2035.08.18, 2040.08.18, 2045.08.18],
    "values":[1.3721, 1.4354, 1.5014, 1.5543, 1.6651, 1.6994, 1.8381,
              1.9226, 1.9565, 2.1438, 2.1934] / 100.0
}
discountCurve = parseMktData(curve)
//step3: 调用定价函数
pricingDate = 2025.08.18
npv = bondPricer(instrument, pricingDate, discountCurve)
//step4: 打印结果
print(npv)
/* output:
100.574981714653844
*/
```

**例 3：固定利率债定价**
( 240021.IB
**，**
[240021\_24附息国债21\_2024年记账式附息(二十一期)国债\_中国货币网](https://www.chinamoney.com.cn/chinese/zqjc/?bondDefinedCode=degib40021)
**）**

```dolphindb
//step1: 生成instrument
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "FixedRateBond",
    "instrumentId": "240021.IB",
    "start": 2024.10.25,
    "maturity": 2025.10.25,
    "issuePrice": 100,
    "coupon": 0.0133,
    "frequency": "Annual",
    "dayCountConvention": "ActualActualISDA"
}
instrument = parseInstrument(bond)
//step2: 准备定价需要用到的曲线
/*
 因为该债券为国债，所以discoutCurve选取国债收益率曲线（即期）
 数据来源https://www.chinamoney.com.cn/chinese/bkcurvclosedyhis/index.html
*/
curve =  {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_TREASURY_BOND",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Compounded",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    // 0.083 0.25 0.5 1.0 2.0 3.0 5.0 7.0 10.0 15.0 20.0 30.0 40.0 50.0
    "dates":[2025.09.18, 2025.11.18, 2026.02.18, 2026.08.18, 2027.08.18, 2028.08.18, 2030.08.18,
             2032.08.18, 2035.08.18, 2040.08.18, 2045.08.18, 2055.08.18,2065.08.18, 2075.08.18],
    "values":[1.3000, 1.3700, 1.3898, 1.3865, 1.4299, 1.4471, 1.6401,
              1.7654, 1.7966, 1.9930, 2.1834, 2.1397, 2.1987, 2.2225] / 100.0
}
discountCurve = parseMktData(curve)
//step3: 调用定价函数
pricingDate = 2025.08.18
npv = bondPricer(instrument, pricingDate, discountCurve)
//step4: 打印结果
print(npv)
/* output:
101.076528630342707 
*/
```

### 2.2 国债期货定价

国债期货定价 (
[bondFuturesPricer](../funcs/b/bondFuturesPricer.html)
)​
**​**
使用持有成本模型
**​**
​。该模型的基本思想是，购买现货国债并持有至期货交割日的总成本，应等于直接购买国债期货的成本，否则市场就会出现无风险的套利机会。其最核心的公（参考[1]）可以概括为：

​
**​ 国债期货价格 = (现货价格 + 融资成本 - 持有收益) / 转换因子**

这里假设定价日为 2025 年 8 月 18 日， 2025 年 9 月份到期的十年期国债期货 T2509 的最便宜交割券为220010.IB, 该国债期货的定价过程如下：

```dolphindb
//step1: 生成instrument
//交割券信息
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "FixedRateBond",
    "instrumentId": "220010.IB",
    "start": "2022.05.15",
    "maturity": "2032.05.15",
    "issuePrice": 100.0,
    "coupon": 0.0276,
    "frequency": "Semiannual",
    "dayCountConvention": "ActualActualISDA"
}
//国债期货信息
bondFutures = { 
    "productType": "Futures",
    "futuresType": "BondFutures",
    "instrumentId": "T2509",
    "nominal": 100.0,
    "maturity": "2025.09.12",
    "settlement": "2025.09.16",
    "underlying": bond,
    "nominalCouponRate": 0.03
}
instrument = parseInstrument(bondFutures)
//step2: 准备定价需要用到的曲线
//国债收益率曲线(即期)
curve =  {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_TREASURY_BOND",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Compounded",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    // 0.083 0.25 0.5 1.0 2.0 3.0 5.0 7.0 10.0 15.0 20.0 30.0 40.0 50.0
    "dates":[2025.09.18, 2025.11.18, 2026.02.18, 2026.08.18, 2027.08.18, 2028.08.18, 2030.08.18,
             2032.08.18, 2035.08.18, 2040.08.18, 2045.08.18, 2055.08.18,2065.08.18, 2075.08.18],
    "values":[1.3000, 1.3700, 1.3898, 1.3865, 1.4299, 1.4471, 1.6401,
              1.7654, 1.7966, 1.9930, 2.1834, 2.1397, 2.1987, 2.2225] / 100.0
}
discountCurve = parseMktData(curve)
//step3: 调用定价函数
pricingDate = 2025.08.18
npv = bondFuturesPricer(instrument, pricingDate, discountCurve)
//step4: 打印结果
print(npv)
// output:107.940924852555937
```

### 2.3 存款定价

存款定价 (
[irDepositPricer](../funcs/i/irDepositPricer.html)
) 相当于只有一期现金流的债券定价。需要注意的是，存款的计息惯例一般为Actual360，可以在构建 instrument 的时候指定。简单示例如下：

```dolphindb
//step1: 生成instrument
deposit =  {
    "productType": "Cash",
    "assetType": "Deposit",
    "start": 2025.07.15,
    "maturity": 2025.10.15,
    "rate": 0.02,
    "dayCountConvention": "Actual360",
    "notionalAmount":1E6,
    "notionalCurrency": "CNY",
    "payReceive": "Receive"
}
instrument = parseInstrument(deposit)
//step2: 准备定价需要用到的曲线
curve = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_FR_007",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",     
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates":[2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20, 2025.11.20, 
             2026.02.24, 2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20,2028.08.21],
    "values":[1.4759, 1.5331, 1.5697, 1.5239, 1.4996, 1.5144, 1.5209,
              1.5539, 1.5461, 1.5316, 1.5376, 1.5435,1.5699] / 100
}
discountCurve = parseMktData(curve)
//step3: 调用定价函数
pricingDate = 2025.08.18
irDepositPricer(instrument, pricingDate, discountCurve)
// output:1002699.4865622655
```

### 2.4 标准利率互换定价

利率互换是比较常见的交易类型，目前仅支持以 FR\_007 和 SHIBOR\_3M 为浮动参考利率的人民币利率互换合约，两者合计占人民币利率互换九成以上的交易量。

利率互换的两条腿相当于两个债券（一个固定利率债，一个浮动利率债）。对于一个接受固定利率，支付浮动利率的利率互换持有方，其定价公式为

npv = npv\_fixed - npv\_floating

利率互换定价（
[irFixedFloatingSwapPricer](../funcs/i/irFixedFloatingSwapPricer.html)
）需要提供浮动利率参考的历史数据，需要传入浮动参考利率的历史数据，用于计算定价日后的第一期浮动利率。示例如下：

```dolphindb
//step1: 生成instrument
irs =  {
    "productType": "Swap",
    "swapType": "IrSwap",
    "irSwapType": "IrFixedFloatingSwap",
    "start": 2025.06.16,
    "maturity": 2028.06.16,
    "frequency": "Quarterly",
    "fixedRate": 0.018,
    "calendar": "CFET", 
    "fixedDayCountConvention": "Actual365",
    "floatingDayCountConvention": "Actual365",
    "payReceive": "Pay",
    "iborIndex": "FR_007",
    "spread": 0.0001,
    "notionalAmount":1E8,
    "notionalCurrency": "CNY"
}
instrument = parseInstrument(irs)
//step2: 准备定价需要用到的曲线
curve = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "curveName": "CNY_FR_007",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",     
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates":[2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20, 2025.11.20, 
             2026.02.24, 2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20,2028.08.21],
    "values":[1.4759, 1.5331, 1.5697, 1.5239, 1.4996, 1.5144, 1.5209,
              1.5539, 1.5461, 1.5316, 1.5376, 1.5435,1.5699] / 100
}
/*
为了计算定价日后面的第一笔现金流用到的浮动利率，需要传入参考利率的历史数据
因为 FR_007 利率互换的付息频率为季度，建议传入的 FR_007 的历史定盘数据不少于 70 个交易日
*/
fr007HistCurve = {
    "mktDataType": "Curve",
    "curveType": "AssetPriceCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "dates":[2025.05.09, 2025.05.12, 2025.05.13, 2025.05.14, 2025.05.15, 2025.05.16, 2025.05.19, 2025.05.20, 2025.05.21, 2025.05.22,
             2025.05.23, 2025.05.26, 2025.05.27, 2025.05.28, 2025.05.29, 2025.05.30, 2025.06.03, 2025.06.04, 2025.06.05, 2025.06.06,
             2025.06.09, 2025.06.10, 2025.06.11, 2025.06.12, 2025.06.13, 2025.06.16, 2025.06.17, 2025.06.18, 2025.06.19, 2025.06.20,
             2025.06.23, 2025.06.24, 2025.06.25, 2025.06.26, 2025.06.27, 2025.06.30, 2025.07.01, 2025.07.02, 2025.07.03, 2025.07.04,
             2025.07.07, 2025.07.08, 2025.07.09, 2025.07.10, 2025.07.11, 2025.07.14, 2025.07.15, 2025.07.16, 2025.07.17, 2025.07.18,
             2025.07.21, 2025.07.22, 2025.07.23, 2025.07.24, 2025.07.25, 2025.07.28, 2025.07.29, 2025.07.30, 2025.07.31, 2025.08.01,
             2025.08.04, 2025.08.05, 2025.08.06, 2025.08.07, 2025.08.08, 2025.08.11, 2025.08.12, 2025.08.13, 2025.08.14, 2025.08.15
       ],
    "values":[1.6000, 1.5600, 1.5300, 1.5500, 1.5500, 1.6300, 1.6500, 1.6000, 1.5900, 1.5800, 
              1.6300, 1.7000, 1.7000, 1.7000, 1.7500, 1.7500, 1.5900, 1.5800, 1.5700, 1.5600, 
              1.5500, 1.5500, 1.5600, 1.5900, 1.5900, 1.5700, 1.5500, 1.5600, 1.5679, 1.6000, 
              1.5700, 1.8500, 1.8300, 1.8400, 1.8500, 1.9500, 1.6036, 1.5800, 1.5200, 1.5000, 
              1.5000, 1.5100, 1.5100, 1.5300, 1.5200, 1.5500, 1.6000, 1.5400, 1.5400, 1.5000, 
              1.5000, 1.4800, 1.5000, 1.6000, 1.7500, 1.6400, 1.6200, 1.6300, 1.6000, 1.5000, 
              1.4800, 1.4700, 1.4800, 1.4900, 1.4600, 1.4600, 1.4600, 1.4800, 1.4800, 1.4900  
               ]\100
}
curve = parseMktData(curve)
discountCurve = curve
forwardCurve = curve
assetPriceCurve = parseMktData(fr007HistCurve)
//step3: 调用定价函数
// 仅计算 npv
pricingDate = 2025.08.18
npv = irFixedFloatingSwapPricer(instrument, pricingDate, discountCurve, forwardCurve, assetPriceCurve)
print(npv)
// 计算包括 npv、现金流在内的各类指标
setting = {
    "calcCashFlow": true
}
results = irFixedFloatingSwapPricer(instrument, pricingDate, discountCurve, forwardCurve, assetPriceCurve, setting)
print(results)
```

### 2.5 外汇远期定价

外汇远期交易是一种基础的金融衍生工具，主要用于管理汇率风险。外汇远期定价需要传入两种货币的折现曲线和即期汇率作为市场数据。这里给出一个外汇远期定价（
[fxForwardPricer](../funcs/f/fxForwardPricer.html)
）的例子：

```dolphindb
//step1: 生成instrument
fxForward = {
    "productType": "Forward",
    "forwardType": "FxForward",
    "expiry": 2025.12.16,
    "delivery": 2025.12.18,
    "currencyPair": "USDCNY",
    "direction": "Buy",
    "notionalAmount":1E6,
    "notionalCurrency": "USD",
    "strike": 7.1
}
instrument = parseInstrument(fxForward)
//step2: 准备定价需要用到的曲线和即期
curveDates = [2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20,
  2025.11.20, 2026.02.24, 2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20,2028.08.21]
domesticCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[1.5113, 1.5402, 1.5660, 1.5574, 1.5556, 1.5655, 1.5703, 
              1.5934, 1.6040, 1.6020, 1.5928, 1.5842, 1.6068]/100
}
foreignCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": 2025.08.18,
    "currency": "USD",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[4.3345, 4.3801, 4.3119, 4.3065, 4.2922, 4.2196, 4.1599, 
              4.0443, 4.0244, 3.9698, 3.7740, 3.6289, 3.5003]/100
}
domesticCurve = parseMktData(domesticCurveInfo)
foreignCurve = parseMktData(foreignCurveInfo)
spot = 7.1627
//step3: 调用定价函数
pricingDate = 2025.08.18
npv = fxForwardPricer(instrument, pricingDate, spot, domesticCurve, foreignCurve)
//step4: 打印结果
print(npv)
// output: 1919.8118
```

### 2.6 外汇掉期定价

外汇掉期交易是指交易者​​同时进行两笔金额相同、货币相同、但交割期限不同、方向相反​​的外汇交易，相当于两个外汇远期交易组合。外汇掉期定价也需要传入两种货币的折现曲线和即期汇率作为市场数据。这里给出一个外汇掉期定价（
[fxSwapPricer](../funcs/f/fxSwapPricer.html)
）的例子：

```dolphindb
//step1: 生成instrument
pricingDate = 2025.08.18
fxSwap = {
    "productType": "Swap",
    "swapType": "FxSwap",
    "currencyPair": "USDCNY",
    "direction": "Buy",
    "notionalAmount":1E6,
    "notionalCurrency": "USD",
    "nearStrike": 7.15,
    "nearExpiry": pricingDate + 60,
    "nearDelivery": pricingDate + 62,
    "farStrike": 7.18,
    "farExpiry": pricingDate + 180,
    "farDelivery": pricingDate + 182
}
instrument = parseInstrument(fxSwap)
//step2: 准备定价需要用到的曲线和即期
curveDates = [2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20,
  2025.11.20, 2026.02.24, 2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20,2028.08.21]
domesticCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[1.5113, 1.5402, 1.5660, 1.5574, 1.5556, 1.5655, 1.5703, 
              1.5934, 1.6040, 1.6020, 1.5928, 1.5842, 1.6068]/100
}
foreignCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "USD",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[4.3345, 4.3801, 4.3119, 4.3065, 4.2922, 4.2196, 4.1599, 
              4.0443, 4.0244, 3.9698, 3.7740, 3.6289, 3.5003]/100
}
domesticCurve = parseMktData(domesticCurveInfo)
foreignCurve = parseMktData(foreignCurveInfo)
spot = 7.1627
//step3: 调用定价函数
npv = fxSwapPricer(instrument, pricingDate, spot, domesticCurve, foreignCurve)
//step4: 打印结果
print(npv)
// output： 84379.328782705269986
```

### 2.7 外汇欧式期权定价

外汇欧式期权​​是一种金融衍生工具，它赋予持有者在​​未来某个特定日期（到期日）​​，以​​事先约定的汇率（行权价）​​，买入或卖出一定数量某种货币对的​​权利​​，但​​没有义务​。外汇欧式期权定价除了需要传入两种货币的折现曲线和即期汇率外，还需要传入波动率曲面作为市场数据。

目前仅支持了 BlackScholes 模型的解析解 (Analytic) 方法。这里给出一个外汇欧式期权定价（
[fxEuropeanOptionPricer](../funcs/f/fxEuropeanOptionPricer.html)
）的例子：

```dolphindb
//step1: 生成instrument
pricingDate = 2025.08.18
ccyPair = "USDCNY"
option = {
    "productType": "Option",
    "optionType": "EuropeanOption",
    "assetType": "FxEuropeanOption",
    "notionalAmount":1E6,
    "notionalCurrency": "USD",
    "strike": 7.2,
    "maturity": 2025.10.28,
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": ccyPair
}
instrument = parseInstrument(option)
//step2: 准备定价需要用到的曲面、曲线和即期
quoteTerms = ['1d', '1w', '2w', '3w', '1M', '2M', '3M', '6M', '9M', '1y', '18M', '2y', '3y']
quoteNames = ["ATM", "D25_RR", "D25_BF", "D10_RR", "D10_BF"]
quotes = [0.030000, -0.007500, 0.003500, -0.010000, 0.005500, 
          0.020833, -0.004500, 0.002000, -0.006000, 0.003800, 
          0.022000, -0.003500, 0.002000, -0.004500, 0.004100, 
          0.022350, -0.003500, 0.002000, -0.004500, 0.004150, 
          0.024178, -0.003000, 0.002200, -0.004750, 0.005500, 
          0.027484, -0.002650, 0.002220, -0.004000, 0.005650, 
          0.030479, -0.002500, 0.002400, -0.003500, 0.005750, 
          0.035752, -0.000500, 0.002750,  0.000000, 0.006950, 
          0.038108,  0.001000, 0.002800,  0.003000, 0.007550, 
          0.039492,  0.002250, 0.002950,  0.005000, 0.007550, 
          0.040500,  0.004000, 0.003100,  0.007000, 0.007850, 
          0.041750,  0.005250, 0.003350,  0.008000, 0.008400, 
          0.044750,  0.006250, 0.003400,  0.009000, 0.008550]
quotes = reshape(quotes, size(quoteNames):size(quoteTerms)).transpose()
curveDates = [2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20,
  2025.11.20, 2026.02.24, 2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20,2028.08.21]
domesticCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[1.5113, 1.5402, 1.5660, 1.5574, 1.5556, 1.5655, 1.5703, 
              1.5934, 1.6040, 1.6020, 1.5928, 1.5842, 1.6068]/100
}
foreignCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "USD",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",  
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": curveDates,
    "values":[4.3345, 4.3801, 4.3119, 4.3065, 4.2922, 4.2196, 4.1599, 
              4.0443, 4.0244, 3.9698, 3.7740, 3.6289, 3.5003]/100
}
surf = fxVolatilitySurfaceBuilder(pricingDate, ccyPair, quoteNames, quoteTerms, quotes, spot, domesticCurve, foreignCurve)
domesticCurve = parseMktData(domesticCurveInfo)
foreignCurve = parseMktData(foreignCurveInfo)
spot = 7.1627
//step3: 调用定价函数
npv = fxEuropeanOptionPricer(instrument, pricingDate, spot, domesticCurve, foreignCurve, surf)
//step4: 打印结果
print(npv)
//output: 1693.99192059959023
```

### 2.8 商品期货欧式期权定价

该期权是以商品期货合约为标的的欧式期权。对于此类欧式期权，我们提供Black76模型的解析解。同时支持计算 delta/gamma/vega/theta/rho五个风险指标。这里给出一个商品期货欧式期权定价（
[cmFutEuropeanOptionPricer](../funcs/c/cmfuteuropeanoptionpricer.html)
）的例子：

```dolphindb
pricingDate = 2019.07.08
spot = 2800.0
strike = spot * 1.2
nominal = 1.0
// Discount curve (CNY FR007) — zero rates
discountCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": [pricingDate+2, pricingDate+8, pricingDate+93, pricingDate+185, pricingDate+276, pricingDate+367,
              pricingDate+732, pricingDate+1099, pricingDate+1463, pricingDate+1828, pricingDate+2558, pricingDate+3654],
    "values": [0.0145993931630537, 0.0229075517972275, 0.0253020667393029, 0.0257564866303201,
               0.0259751440992468, 0.0260355181479988, 0.0265336263144786, 0.0272721454114050,
               0.0282024453631075, 0.0290231222075799, 0.0304665029488732, 0.0319855013976250]
}
discountCurve = parseMktData(discountCurveInfo)
// Futures price curve (Soymeal)
futPriceCurveInfo = {
    "mktDataType": "Curve",
    "curveType": "AssetPriceCurve",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "asset": "SOY_MEAL",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "dates": [2019.09.16, 2019.11.14, 2019.12.13, 2020.01.15, 2020.03.13],
    "values": [2784, 2821, 2772, 2847, 2775]
}
futPriceCurve = parseMktData(futPriceCurveInfo)
// Option expiries, futures maturities, strikes, market prices, payoff types
optionExpiries = [2019.08.07, 2019.10.11, 2019.11.07, 2019.12.06, 2020.02.07]
futMaturities = [2019.09.16, 2019.11.14, 2019.12.13, 2020.01.15, 2020.03.13]
strikes = [
    [2600,2650,2700,2750,2800,2850,2900,2950,3000,3050],
    [2600,2650,2700,2750,2800,2850,2900,2950,3000,3050],
    [2650,2700,2750,2800,2850,2900,2950,3000],
    [2650,2700,2750,2800,2850,2900,2950,3000],
    [2600,2650,2700,2750,2800,2850,2900]
]
optionPrices = [
    [9,17,30,48.5,57,37.5,23,13.5,7.5,4],
    [29,41.5,56.5,75.5,98,95.5,75,58.5,44.5,33.5],
    [50,68.5,90.5,89,69,52.5,39,29],
    [56,72,91,113,134.5,112.5,93,76.5],
    [58.5,75.5,95,118,119.5,98.5,80.5]
]
payoffTypes = [
    ["Put","Put","Put","Put","Call","Call","Call","Call","Call","Call"],
    ["Put","Put","Put","Put","Put","Call","Call","Call","Call","Call"],
    ["Put","Put","Put","Call","Call","Call","Call","Call"],
    ["Put","Put","Put","Put","Call","Call","Call","Call"],
    ["Put","Put","Put","Put","Call","Call","Call"]
]
// Build vol surface from quotes
volSurf = cmFutVolatilitySurfaceBuilder(pricingDate, futMaturities, optionExpiries, strikes, optionPrices, payoffTypes, discountCurve, futPriceCurve)
print(volSurf)
// Instrument
cmFutEuropeanOption = {
    "productType": "Option",
    "optionType": "EuropeanOption",
    "assetType": "CmFutEuropeanOption",
    "instrumentId": "SOYMEAL_CALL",
    "notionalAmount": nominal,
    "notionalCurrency": "CNY",
    "strike": strike,
    "maturity": pricingDate + 180,
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": "SOY_MEAL"
}
instrument = parseInstrument(cmFutEuropeanOption)
// Price
setting={"calcDelta": true, "calcGamma": true, "calcVega": true, "calcTheta": true, "calcRho": true}
result = cmFutEuropeanOptionPricer(instrument, pricingDate, spot, discountCurve, volSurf, setting)
print(result)
```

### 2.9 商品期货美式期权定价

该期权是以商品期货合约为标的的美式期权。国内商品期货交易所交易的期权品种皆为此类。对于此类期权，我们提供Black76/BAW模型的解析解，也提供美式二叉树解法，同时支持计算 delta/gamma/vega/theta/rho五个风险指标。这里给出一个商品期货美式期权定价（
[cmFutAmericanOptionPricer](../funcs/c/cmfutamericanoptionpricer.html)
）的例子：

```dolphindb
// ================================================================
// AUTO-GENERATED DolphinDB Script
// Function: cmFutAmericanOptionPricer  商品期货美式期权定价示例
// Underlying: 上海期货交易所铜期货期权（cu）
// PricingDate: 2026-02-13
//
// 数据来源:
//   期货结算价: akshare get_futures_daily(market='SHFE')
//   期权结算价: akshare option_hist_shfe('铜期权', '20260213')
//   利率曲线: 中国货币网 外币隐含利率曲线（CNY, USD.CNY/Shibor/掉期点）
//                https://www.chinamoney.com.cn/chinese/bkcurvuiruuh/
//                API: POST /ags/ms/cm-u-bk-fx/IuirCurvHis  2026-02-13
//
// 定价标的: CU2605 铜期货美式看涨 Call
//               strike=102000  opt_expiry=2026-04-24
//               fut_price=101230
// ================================================================
pricingDate   = 2026.02.13
referenceDate = pricingDate
// ------------------------------------------------------------------
// 1. 折现曲线 (CNY_FR_007) ── 中国货币网外币隐含利率曲线
//    数据源: https://www.chinamoney.com.cn/chinese/bkcurvuiruuh/
//    USD.CNY / Shibor / 即期询价报价均值 / 掉期点  →  rmbRateStr 字段
// ------------------------------------------------------------------
discountCurveDict = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": referenceDate,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates": [referenceDate + 1, referenceDate + 7, referenceDate + 14, referenceDate + 21, referenceDate + 30, referenceDate + 61, referenceDate + 91, referenceDate + 182, referenceDate + 273, referenceDate + 365, referenceDate + 547, referenceDate + 730, referenceDate + 1095],
    "values": [0.016134, 0.016107, 0.016102, 0.016102, 0.016102, 0.016103, 0.016029, 0.015832, 0.015889, 0.015898, 0.015561, 0.015583, 0.015892],
    "name": "CNY_FR_007"
}
discountCurve = parseMktData(discountCurveDict)
// ------------------------------------------------------------------
// 2. 期货价格曲线 (AssetPriceCurve)
//    各到期月份铜期货结算价
// ------------------------------------------------------------------
futPriceCurveDict = {
    "mktDataType": "Curve",
    "curveType": "AssetPriceCurve",
    "referenceDate": referenceDate,
    "currency": "CNY",
    "asset": "CU",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "dates": [2026.04.15, 2026.05.15, 2026.06.15, 2026.07.15, 2026.08.17, 2026.09.15],
    "values": [100980.0, 101230.0, 101240.0, 101100.0, 101230.0, 101250.0]
}
futPriceCurve = parseMktData(futPriceCurveDict)
// ------------------------------------------------------------------
// 3. 期权市场数据 ── 构建波动率曲面
//    到期日数: 6
//    使用虚值期权: K < F → Put, K >= F → Call
// ------------------------------------------------------------------
optionExpiries = [2026.03.25, 2026.04.24, 2026.05.25, 2026.06.24, 2026.07.27, 2026.08.25]
futMaturities  = [2026.04.15, 2026.05.15, 2026.06.15, 2026.07.15, 2026.08.17, 2026.09.15]
strikes = [
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000],
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000],
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000],
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000],
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000],
    [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000]
]
optionPrices = [
    [118, 208, 344, 544, 826, 1204, 1702, 2322, 3078, 3986, 4012, 3192, 2506, 1946, 1490, 1124, 836, 612, 442, 316],
    [396, 580, 826, 1144, 1552, 2052, 2652, 3360, 4178, 5108, 5382, 4536, 3792, 3146, 2590, 2114, 1718, 1388, 1114, 886],
    [828, 1112, 1464, 1888, 2392, 2980, 3660, 4440, 5312, 6276, 6570, 5712, 4950, 4276, 3672, 3132, 2664, 2264, 1908, 1596],
    [1218, 1566, 1980, 2474, 3048, 3702, 4432, 5240, 6142, 7138, 7308, 6450, 5696, 5006, 4370, 3820, 3324, 2870, 2490, 2146],
    [2054, 2508, 3014, 3614, 4272, 4986, 5792, 6666, 7586, 8616, 8924, 8076, 7304, 6566, 5926, 5306, 4768, 4258, 3808, 3390],
    [1938, 2374, 2876, 3460, 4104, 4804, 5608, 6472, 7386, 8410, 8734, 7886, 7116, 6378, 5742, 5132, 4592, 4094, 3644, 3240]
]
payoffTypes = [
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"]
]
// ------------------------------------------------------------------
// 4. 构建波动率曲面 ── BAW 公式 + SVI 模型
//    使用 BAW 公式计算美式期权隐含波动率
// ------------------------------------------------------------------
volSurf = cmFutVolatilitySurfaceBuilder(
    referenceDate, futMaturities, optionExpiries,
    strikes, optionPrices, payoffTypes,
    discountCurve, futPriceCurve,
    formula="BAW", model="SVI",
    surfaceName="cu_vol_surface_20260213"
)
print(volSurf)
// ------------------------------------------------------------------
// 5. 定义定价合约 ── 铜期货美式看涨期权
//    标的: CU2605  行权价: 102000  到期: 2026-04-24
// ------------------------------------------------------------------
cmFutAmericanOption = {
    "productType": "Option",
    "optionType": "AmericanOption",
    "assetType": "CmFutAmericanOption",
    "instrumentId": "CU2605C102000",
    "notionalAmount": 5.0,
    "notionalCurrency": "CNY",
    "strike": 102000.0,
    "maturity": 2026.04.24,
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": "CU2605",
    "domesticCurve": "CNY_FR_007"
}
instrument = parseInstrument(cmFutAmericanOption)
// ------------------------------------------------------------------
// 6. 定价 ── 单合约 NPV (BAW 模型)
// ------------------------------------------------------------------
spot = 101230.0
npv = cmFutAmericanOptionPricer(instrument, pricingDate, spot, discountCurve, volSurf, model="BAW")
print("NPV = " + string(npv))
// ------------------------------------------------------------------
// 7. 定价 ── 含希腊字母 (Greeks)
// ------------------------------------------------------------------
setting = {
    "calcDelta": true,
    "calcGamma": true,
    "calcVega": true,
    "calcTheta": true,
    "calcRho": true
}
result = cmFutAmericanOptionPricer(instrument, pricingDate, spot, discountCurve, volSurf, setting, model="BAW")
print(result)
// ------------------------------------------------------------------
// 8. 批量定价 ── 对 CU2605 到期的多个行权价 Call 合约定价
// ------------------------------------------------------------------
allStrikes = [82000, 84000, 86000, 88000, 90000, 92000, 94000, 96000, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 112000, 114000, 116000, 118000, 120000]
results = array(DOUBLE, 0)
for (k in allStrikes) {
    iDict = {
        "productType": "Option",
        "optionType": "AmericanOption",
        "assetType": "CmFutAmericanOption",
        "instrumentId": "CU2605C" + string(int(k)),
        "notionalAmount": 5.0,
        "notionalCurrency": "CNY",
        "strike": k,
        "maturity": 2026.04.24,
        "payoffType": "Call",
        "dayCountConvention": "Actual365",
        "underlying": "CU2605",
        "domesticCurve": "CNY_FR_007"
    }
    iOpt = parseInstrument(iDict)
    results.append!(cmFutAmericanOptionPricer(iOpt, pricingDate, spot, discountCurve, volSurf, model="BAW"))
}
t = table(allStrikes as strike, results as npv)
print(t)
```

### 2.10 权益类欧式期权定价

权益类期权的标的包括 **股票、股指和 ETF**
，这里我们对于不同品种的乘数细节不做限制，用户可以根据需要去适配。国内交易所的ETF和股指期权皆为此类。对于此类欧式期权，我们提供 BlackScholes
模型的解析解，同时支持 Greeks 计算。这里给出一个权益类欧式期权定价（ [eqEuropeanOptionPricer](../funcs/e/eqeuropeanoptionpricer.html)
）的例子：

```dolphindb
// ================================================================
// AUTO-GENERATED DolphinDB Script
// Function: eqEuropeanOptionPricer  欧式期权定价示例
// Underlying: 上证50ETF（510050.SH）
// PricingDate: 2026-02-13
//
// 数据来源:
//   现货价格: akshare fund_etf_hist_sina('sh510050')     → 3.1140
//   期权链/IV: akshare option_risk_indicator_sse('20260213')
//               → Black-Scholes 重建期权结算价
//   利率曲线: 中国货币网 外币隐含利率曲线（CNY, USD.CNY/Shibor/掉期点）
//               https://www.chinamoney.com.cn/chinese/bkcurvuiruuh/
//               API: POST /ags/ms/cm-u-bk-fx/IuirCurvHis  2026-02-13
//
// 定价标的: 看涨 Call  strike=3.2000  expiry=2026-03-25
// ================================================================
pricingDate   = 2026.02.13
referenceDate = pricingDate
// ------------------------------------------------------------------
// 1. 现货价格
// ------------------------------------------------------------------
spot = 3.1140
// ------------------------------------------------------------------
// 2. 定义定价合约  (近月 ATM/轻虚值看涨期权)
// ------------------------------------------------------------------
optionDict = {
    "productType": "Option",
    "optionType": "EuropeanOption",
    "assetType": "EqEuropeanOption",
    "notionalCurrency": "CNY",
    "notionalAmount": 10000,
    "strike": 3.2000,
    "maturity": 2026.03.25,
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": "510050"
}
option = parseInstrument(optionDict)
// ------------------------------------------------------------------
// 3. 期权链原始数据  (用于构建股息曲线与波动率曲面)
//    到期日序列: 2026.02.25 | 2026.03.25 | 2026.06.24 | 2026.09.23
//    行权价区间: [2.85, 3.60]
// ------------------------------------------------------------------
termDates = [2026.02.25, 2026.03.25, 2026.06.24, 2026.09.23]
callPrices = matrix(
    [0.2655, 0.2155, 0.1656, 0.1156, 0.0318, 0.0039, 0.0015, 0.0008, 0.0003, 0.0001],
    [0.2690, 0.2248, 0.1770, 0.1385, 0.0697, 0.0303, 0.0128, 0.0069, 0.0046, 0.0036],
    [0.3030, 0.2655, 0.2278, 0.1970, 0.1431, 0.0991, 0.0677, 0.0479, 0.0346, 0.0254],
    [0.3330, 0.2987, 0.2681, 0.2388, 0.1883, 0.1448, 0.1139, 0.0899, 0.0715, 0.0574]
)
putPrices = matrix(
    [0.0004, 0.0009, 0.0021, 0.0045, 0.0218, 0.0939, 0.1901, 0.2896, 0.3908, 0.4916],
    [0.0125, 0.0165, 0.0229, 0.0316, 0.0616, 0.1250, 0.2029, 0.2967, 0.3962, 0.4948],
    [0.0396, 0.0507, 0.0634, 0.0798, 0.1253, 0.1814, 0.2499, 0.3321, 0.4175, 0.5077],
    [0.0651, 0.0798, 0.0973, 0.1180, 0.1662, 0.2250, 0.2952, 0.3651, 0.4508, 0.5342]
)
strikes = matrix(
    [2.8500, 2.9000, 2.9500, 3.0000, 3.1000, 3.2000, 3.3000, 3.4000, 3.5000, 3.6000],
    [2.8500, 2.9000, 2.9500, 3.0000, 3.1000, 3.2000, 3.3000, 3.4000, 3.5000, 3.6000],
    [2.8500, 2.9000, 2.9500, 3.0000, 3.1000, 3.2000, 3.3000, 3.4000, 3.5000, 3.6000],
    [2.8500, 2.9000, 2.9500, 3.0000, 3.1000, 3.2000, 3.3000, 3.4000, 3.5000, 3.6000]
)
// ------------------------------------------------------------------
// 4. 折现曲线  ── 中国货币网 外币隐含利率曲线 CNY 利率（2026-02-13）
//    数据源: https://www.chinamoney.com.cn/chinese/bkcurvuiruuh/
//    USD.CNY / Shibor / 即期询价报价均值 / 掉期点  →  rmbRateStr 字段
// ------------------------------------------------------------------
discountCurveDict = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "curveName": "CNY_FR_007",
    "referenceDate": referenceDate,
    "currency": "CNY",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "dates": [referenceDate + 1, referenceDate + 7, referenceDate + 14, referenceDate + 21, referenceDate + 30, referenceDate + 61, referenceDate + 91, referenceDate + 182, referenceDate + 273, referenceDate + 365, referenceDate + 547, referenceDate + 730, referenceDate + 1095],
    "values": [0.016134, 0.016107, 0.016102, 0.016102, 0.016102, 0.016103, 0.016029, 0.015832, 0.015889, 0.015898, 0.015561, 0.015583, 0.015892]
}
discountCurve = parseMktData(discountCurveDict)
// ------------------------------------------------------------------
// 5. 股息曲线  ── Call-Put 平价隐含法 (CallPutParity)
// ------------------------------------------------------------------
dividendCurve = eqDividendCurveBuilder(
    referenceDate, termDates, "CallPutParity", ,
    callPrices, putPrices, strikes, spot, discountCurve,
    "Actual365", "510050"
)
// ------------------------------------------------------------------
// 6. 波动率曲面  ── SABR 模型，使用虚值期权
//    行权价 < Spot → OTM Put；行权价 >= Spot → OTM Call
// ------------------------------------------------------------------
optionExpiries = termDates
optionPrices = matrix(
    [0.0004, 0.0009, 0.0021, 0.0045, 0.0218, 0.0039, 0.0015, 0.0008, 0.0003, 0.0001],
    [0.0125, 0.0165, 0.0229, 0.0316, 0.0616, 0.0303, 0.0128, 0.0069, 0.0046, 0.0036],
    [0.0396, 0.0507, 0.0634, 0.0798, 0.1253, 0.0991, 0.0677, 0.0479, 0.0346, 0.0254],
    [0.0651, 0.0798, 0.0973, 0.1180, 0.1662, 0.1448, 0.1139, 0.0899, 0.0715, 0.0574]
)
payoffTypes = matrix(
    ["Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call"]
)
volSurface = eqVolatilitySurfaceBuilder(
    referenceDate,
    optionExpiries,
    strikes,
    optionPrices,
    payoffTypes,
    spot,
    discountCurve,
    dividendCurve,
    "SABR",
    "50ETF_SABR_20260213"
)
// ------------------------------------------------------------------
// 7. 定价 ── 单合约 NPV
// ------------------------------------------------------------------
npv = eqEuropeanOptionPricer(option, pricingDate, spot, discountCurve, dividendCurve, volSurface)
print("NPV = " + string(npv))
// ------------------------------------------------------------------
// 8. 定价 ── 含希腊字母 (Greeks)
// ------------------------------------------------------------------
setting = {
    "calcDelta": true,
    "calcGamma": true,
    "calcVega": true,
    "calcTheta": true,
    "calcRhoIr": true,
    "calcRhoDividend": true
}
result = eqEuropeanOptionPricer(option, pricingDate, spot, discountCurve, dividendCurve, volSurface, setting)
print(result)
// ------------------------------------------------------------------
// 9. 批量定价 ── 对 2026-03-25 到期的全部公共行权价 Call 合约
// ------------------------------------------------------------------
allStrikes = [2.8500, 2.9000, 2.9500, 3.0000, 3.1000, 3.2000, 3.3000, 3.4000, 3.5000, 3.6000]
results = array(DOUBLE, 0)
for (k in allStrikes) {
    iDict = {
        "productType": "Option",
        "optionType": "EuropeanOption",
        "assetType": "EqEuropeanOption",
        "notionalCurrency": "CNY",
        "notionalAmount": 10000,
        "strike": k,
        "maturity": 2026.03.25,
        "payoffType": "Call",
        "dayCountConvention": "Actual365",
        "underlying": "510050"
    }
    iOpt = parseInstrument(iDict)
    results.append!(eqEuropeanOptionPricer(iOpt, pricingDate, spot, discountCurve, dividendCurve, volSurface))
}
t = table(allStrikes as strike, results as npv)
print(t)
```

### 2.11 权益类美式期权定价

股票期权大多数为美式期权。对于此类期权，我们提供 BlackScholes/BAW 模型的解析解，也提供美式二叉树解法，同时支持 Greeks
计算。这里给出一个权益类美式期权定价（ [eqAmericanOptionPricer](../funcs/e/eqamericanoptionpricer.html) ）的例子：

```dolphindb
//腾讯股票期权定价
referenceDate = 2026.02.13
// 1. Discount Curve (HKD Proxy - Simplified)
// 注意：实际生产中应使用HIBOR或OIS曲线
discountCurveDict = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "curveName": "HKD_RF",
    "referenceDate": referenceDate,
    "currency": "HKD",
    "dayCountConvention": "Actual365",
    "compounding": "Continuous",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "dates": [
        referenceDate + 1, referenceDate + 30, referenceDate + 90,
        referenceDate + 180, referenceDate + 365
    ],
    "values":[0.04, 0.04, 0.04, 0.04, 0.04]
}
discountCurve = parseMktData(discountCurveDict)
// 2. Data Preparation
spot = 532.0
termDates = [2026.02.20, 2026.02.26, 2026.03.30, 2026.04.29, 2026.05.28, 2026.06.29, 2026.09.29, 2026.12.30]
// Matrices are ensured to be dense (no zeros) by Python preprocessing
callPrices = matrix(
    [102.240, 92.250, 82.270, 72.300, 62.360, 52.480, 42.710, 33.180, 24.170, 15.940, 9.000, 4.600, 2.130, 0.960, 0.370, 0.130, 0.050, 0.020, 0.010, 0.010],
    [102.480, 92.530, 82.620, 72.750, 62.980, 53.350, 43.970, 35.430, 26.800, 19.250, 12.390, 8.200, 5.010, 3.030, 1.710, 0.940, 0.490, 0.250, 0.130, 0.070],
    [105.350, 94.410, 84.930, 75.670, 66.690, 59.800, 50.880, 41.900, 34.080, 29.030, 23.600, 18.700, 14.700, 11.470, 8.880, 7.000, 5.320, 4.000, 2.990, 2.220],
    [107.770, 96.450, 87.340, 78.510, 70.000, 61.880, 55.250, 46.990, 41.510, 34.530, 29.120, 24.370, 20.000, 16.900, 13.980, 11.410, 9.320, 7.760, 6.500, 5.320],
    [109.270, 97.890, 89.050, 80.500, 72.290, 64.460, 57.080, 50.140, 45.000, 38.800, 33.130, 28.330, 24.220, 20.630, 17.580, 14.840, 12.540, 10.560, 8.850, 7.440],
    [110.210, 98.620, 90.010, 81.730, 73.930, 66.430, 59.420, 52.930, 47.380, 42.070, 36.780, 32.290, 28.310, 24.260, 21.250, 18.380, 15.900, 13.610, 11.710, 10.000],
    [115.610, 107.450, 96.760, 89.450, 82.610, 75.990, 69.870, 63.990, 58.540, 54.680, 49.600, 45.520, 40.960, 36.480, 33.520, 30.130, 27.110, 24.080, 21.680, 19.310],
    [124.400, 116.880, 109.390, 99.560, 92.910, 89.300, 82.750, 77.110, 69.700, 66.470, 61.260, 56.670, 52.370, 48.220, 44.480, 40.740, 37.360, 34.350, 31.340, 28.570]
)
putPrices = matrix(
    [0.010, 0.010, 0.030, 0.050, 0.110, 0.210, 0.460, 0.880, 1.750, 3.450, 6.570, 12.100, 19.820, 28.260, 38.190, 48.020, 58.000, 68.000, 78.000, 88.000],
    [0.050, 0.090, 0.160, 0.290, 0.510, 0.900, 1.480, 2.390, 3.930, 6.260, 10.000, 15.350, 21.820, 30.000, 39.150, 48.500, 58.190, 68.000, 80.340, 88.000],
    [0.560, 0.900, 1.410, 2.140, 3.160, 4.540, 6.360, 8.640, 11.390, 14.720, 18.710, 24.150, 30.180, 37.360, 44.600, 53.900, 61.660, 70.100, 80.340, 88.940],
    [1.310, 1.960, 2.840, 4.000, 5.470, 7.000, 9.210, 11.950, 15.110, 18.850, 23.340, 28.440, 34.710, 41.520, 48.300, 57.590, 64.690, 73.180, 81.860, 90.830],
    [2.860, 3.870, 5.230, 6.730, 8.460, 10.740, 13.480, 16.630, 20.240, 24.470, 29.080, 34.410, 40.600, 47.430, 54.580, 62.650, 70.440, 78.580, 86.920, 95.580],
    [3.790, 5.140, 6.750, 8.680, 10.870, 13.690, 16.300, 19.650, 23.400, 27.920, 32.950, 38.280, 44.180, 50.760, 57.030, 65.510, 73.230, 78.580, 86.920, 97.520],
    [8.130, 10.140, 12.540, 15.140, 17.750, 20.910, 24.310, 28.300, 32.340, 37.020, 42.040, 47.690, 53.480, 60.030, 66.160, 73.900, 80.970, 88.120, 95.810, 101.990],
    [14.020, 15.890, 18.190, 21.170, 24.270, 27.800, 31.600, 35.490, 40.040, 44.910, 49.510, 54.850, 60.560, 67.000, 72.830, 78.360, 84.930, 94.000, 102.120, 109.690]
)
strikes = matrix(
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00],
    [430.00, 440.00, 450.00, 460.00, 470.00, 480.00, 490.00, 500.00, 510.00, 520.00, 530.00, 540.00, 550.00, 560.00, 570.00, 580.00, 590.00, 600.00, 610.00, 620.00]
)
optionPrices = matrix(
    [0.010, 0.010, 0.030, 0.050, 0.110, 0.210, 0.460, 0.880, 1.750, 3.450, 6.570, 4.600, 2.130, 0.960, 0.370, 0.130, 0.050, 0.020, 0.010, 0.010],
    [0.050, 0.090, 0.160, 0.290, 0.510, 0.900, 1.480, 2.390, 3.930, 6.260, 10.000, 8.200, 5.010, 3.030, 1.710, 0.940, 0.490, 0.250, 0.130, 0.070],
    [0.560, 0.900, 1.410, 2.140, 3.160, 4.540, 6.360, 8.640, 11.390, 14.720, 18.710, 18.700, 14.700, 11.470, 8.880, 7.000, 5.320, 4.000, 2.990, 2.220],
    [1.310, 1.960, 2.840, 4.000, 5.470, 7.000, 9.210, 11.950, 15.110, 18.850, 23.340, 24.370, 20.000, 16.900, 13.980, 11.410, 9.320, 7.760, 6.500, 5.320],
    [2.860, 3.870, 5.230, 6.730, 8.460, 10.740, 13.480, 16.630, 20.240, 24.470, 29.080, 28.330, 24.220, 20.630, 17.580, 14.840, 12.540, 10.560, 8.850, 7.440],
    [3.790, 5.140, 6.750, 8.680, 10.870, 13.690, 16.300, 19.650, 23.400, 27.920, 32.950, 32.290, 28.310, 24.260, 21.250, 18.380, 15.900, 13.610, 11.710, 10.000],
    [8.130, 10.140, 12.540, 15.140, 17.750, 20.910, 24.310, 28.300, 32.340, 37.020, 42.040, 45.520, 40.960, 36.480, 33.520, 30.130, 27.110, 24.080, 21.680, 19.310],
    [14.020, 15.890, 18.190, 21.170, 24.270, 27.800, 31.600, 35.490, 40.040, 44.910, 49.510, 56.670, 52.370, 48.220, 44.480, 40.740, 37.360, 34.350, 31.340, 28.570]
)
payoffTypes = matrix(
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"],
    ["Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Put", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call", "Call"]
)
// 3. Build Dividend Curve (CallPutParity)
// 使用 Call-Put Parity 从期权价格中隐含出分红（股息）曲线
dividendCurve = eqDividendCurveBuilder(
    referenceDate, termDates, "CallPutParity", ,
    callPrices, putPrices, strikes, spot, discountCurve, "Actual365"
)
// 4. Build Volatility Surface (SVI Model)
// 构建波动率曲面
surface = eqVolatilitySurfaceBuilder(
        referenceDate,
        termDates,
        strikes,
        optionPrices,
        payoffTypes,
        spot,
        discountCurve,
        dividendCurve,
        "SVI"
)
// 5. Pricing Test: eqAmericanOptionPricer
optionDict = {
    "productType": "Option",
    "optionType": "AmericanOption",
    "assetType": "EqAmericanOption",
    "notionalCurrency": "HKD",    // price currency
    "notionalAmount": 1,          // 份数      
    "strike": 530.0,
    "maturity": 2026.02.24,
    "payoffType": "Call",
    "dayCountConvention": "Actual365",
    "underlying": "00700.HK"
}
instrument = parseInstrument(optionDict)
res = eqAmericanOptionPricer(
        instrument,
        referenceDate,
        spot,
        discountCurve,
        dividendCurve,
        surface,
        setting={"calcDelta": true, "calcGamma": true, "calcVega": true, "calcTheta": true, "calcRho": true, "calcRhoIr": true, "calcRhoDividend": true}
)
print(res)
```

## 3.特殊定价接口

金融机构每天需要对持有的交易头寸进行定价。对于持有的不同资产，金融机构需要根据不同交易类型分别调用对应的定价函数，如 IRS 交易需要去调用利率互换定价函数，FxSwap 交易需要去调用外汇掉期定价函数，需要写很多 if-else 判断。除此之外，不同的定价函数需要的市场数据（Spot/Curve/VolSurf）也不一样。同一种交易类型，入参类型相同，也需要根据标的等信息适配不同的市场数据。用户在使用的时候需要做很多配置，随着交易种类和数量的增加，这种配置方法很不方便而且容易出错。

针对上述问题，DolphinDB 创新性地提出统一定价接口
[instrumentPricer](../funcs/i/instrumentPricer.html)
。为了方便用户对组合进行定价，我们在前者的基础上，加入头寸信息，提供
[portfolioPricer](../funcs/p/portfolioPricer.html)
接口。下面分别介绍这两个接口。

### 3.1 instrumentPricer

[instrumentPricer](../funcs/i/instrumentPricer.html)
是 DolphinDB 推出的统一定价接口。对于常见的交易产品和市场数据，系统自动提供 instrument 与 marketData 的默认匹配方案，无需额外操作。在特殊场景下，也可自定义匹配，大大提升了灵活性。用户只需要把交易封装成 INSTRUMENT 对象，统一放到一个向量中，将市场数据（曲线/曲面）封装成 MKTDATA 对象，放到一个向量或字典中，系统就能对金融工具进行批量定价，输出 npv 向量。

#### 3.1.1 instrument 和 marketData 的匹配规则

在定价过程中，系统会按照以下优先级确定市场数据：

1. 若
   *instrument*
   中已显式指定市场数据，则直接使用该数据；
2. 若未指定，则系统根据预定义规则自动匹配合适的市场数据。

以下将对不同类型金融工具的匹配规则进行说明。

**债券（Bond）**

债券定价需要用到折现曲线。可以通过 discountCurve 字段指定折现曲线名称，例如：

```dolphindb
bond = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "FixedRateBond",
    "instrumentId": "1382011.IB",
    "start": "2013.01.14",
    "maturity": "2028.01.14",
    "issuePrice": 100.0,
    "coupon": 0.058,
    "frequency": "Annual",
    "dayCountConvention": "ActualActualISDA",
    "currency": "CNY",              //可选字段 
    "subType": "MTN",               //可选字段
    "creditRating": "AAA",          //可选字段
    "discountCurve": "CNY_MTN_AAA"  //可选字段
}
```

折现曲线选择规则如下：

- 如果 discountCurve 已指定，定价函数会直接在
  *marketData*
  中查找对应曲线。
- 如果 discountCurve 未指定：指定了 currency，subType 和 creditRating，系统会选择名为 currency + "\_" + subType + "\_" + creditRating 的折现曲线。指定了 currency，且 subType 为
  `TREASURY_BOND`
  ，
  `CENTRAL_BANK_BILL`
  ，
  `CDB_BOND`
  ，
  `EIBC_BOND`
  ，
  `ADBC_BOND`
  之一，则不需要 creditRating，系统会选择名为 currency + "\_" + subType 的折现曲线。指定了 currency，且 subType 不为
  `TREASURY_BOND`
  ，
  `CENTRAL_BANK_BILL`
  ，
  `CDB_BOND`
  ，
  `EIBC_BOND`
  ，
  `ADBC_BOND`
  之一，同时未指定 creditRating，系统会选择名为 currency + "\_TREASURY\_BOND" 的折现曲线。指定了 currency，且未指定 subType 和 creditRating，系统会选择名为 currency + "\_TREASURY\_BOND" 的折现曲线。currency，subType 和 creditRating 均未指定，系统会选择名为 "CNY\_TREASURY\_BOND" 的折现曲线。

**国债期货（BondFutures）**

无需指定 discountCurve，函数会使用其标的债券（underlying）的 dicountCurve。

**存款（Deposit）**

存款定价仅需指定折现曲线 discountCurve：

- 如果 discountCurve（各个币种的无风险曲线）已指定，则使用指定的曲线进行定价。
- 如果未指定，则根据币种自动匹配折现曲线，规则如下：

| currency | discountCurve |
| --- | --- |
| CNY | CNY\_FR\_007 |
| USD | USD\_SOFR |
| EUR | EUR\_ESTR |

**利率互换（IrFixedFloatingSwap）**

利率互换定价需要传入三条曲线：discountCurve、forwardCurve 和 assetPriceCurve。目前仅支持以 FR\_007 和 SHIBOR\_3M 作为浮动参考利率的利率互换。

- 如果在
  *instrument*
  中指定了相应曲线，则使用指定的曲线进行定价。
- 如果未指定，则根据币种和浮动利率基准自动匹配三条默认曲线，如下表所示：

| currency | iborIndex | discountCurve | forwardCurve | assetPriceCurve |
| --- | --- | --- | --- | --- |
| CNY | FR\_007 | CNY\_FR\_007 | CNY\_FR\_007 | PRICE\_FR\_007 |
| CNY | SHIBOR\_3M | CNY\_FR\_007 | CNY\_SHIBOR\_3M | PRICE\_SHIBOR\_3M |

其中 assetPriceCurve 填入的是浮动参考利率的历史数据，用于计算定价日起第一笔现金流的浮动利率。

**外汇远期（FxForward）/ 外汇掉期（FxSwap）**

这两类线性产品定价需要绑定 domesticCurve 和 foreignCurve，并基于 currencyPair 获取相应的 FxSpot。

- 若在
  *instrument*
  中指定了 domesticCurve 和 foreignCurve，则直接使用用户指定的曲线。
- 若未指定，则系统会根据货币对自动匹配默认曲线，如下表所示：

| currencyPair | domesticCurve | foreignCurve |
| --- | --- | --- |
| USDCNY | CNY\_FR\_007 | USD\_USDCNY\_FX |
| EURCNY | CNY\_FR\_007 | EUR\_EURCNY\_FX |
| EURUSD | USD\_SOFR | EUR\_EURUSD\_FX |

其中 foreignCurve 是根据外汇掉期交易，并结合利率平价公式推导得到的外币隐含即期曲线。

**外汇欧式期权（FxEuropeanOption）**

外汇期权定价除需使用 domesticCurve 与 foreignCurve 外，还依赖 fxSpot 和 volSurf。

这两个市场数据均可根据期权的 underlying（货币对） 自动匹配。

- 若在
  *instrument*
  中明确指定，则优先使用用户提供的 domesticCurve、foreignCurve。
- 若未指定，则系统会根据货币对自动匹配，规则如下：

| currencyPair | fxSpot | domesticCurve | foreignCurve | volSurf |
| --- | --- | --- | --- | --- |
| USDCNY | USDCNY | CNY\_FR\_007 | USD\_USDCNY\_FX | USDCNY |
| EURCNY | EURCNY | CNY\_FR\_007 | EUR\_EURCNY\_FX | EURCNY |
| EURUSD | EURUSD | USD\_SOFR | EUR\_EURUSD\_FX | EURUSD |

#### 3.1.2 使用场景

`instrumentPricer` 适合批量定价的场景。

**（1）投资组合批量定价**

投资组合中通常会有不同类型的交易，例如对于固收交易员来说，他的交易类型可能有债券、国债期货、利率互换等。如何方便又快速地对投资组合中的每一笔交易进行定价，是我们要处理的问题。传统的做法是先按照交易类型分类，然后对每一类采用相应的定价函数逐个进行定价，这种方式繁琐且低效。`instrumentPricer`
可以把每笔交易都封装成一个 INSTRUMENT
对象，所有交易都放到一个向量中。用户只需一次函数调用，就能输出所有交易的定价结果。这里给出一个例子：

```dolphindb
bond1 = {
    "productType": "Cash",
    "assetType": "Bond",
    "bondType": "FixedRateBond",
    "instrumentId": "220010.IB",
    "start": 2020.12.25,
    "maturity": 2031.12.25,
    "coupon": 0.0149,
    "frequency": "Annual",
    "dayCountConvention": "ActualActualISDA",
    "discountCurve": "CNY_TREASURY_BOND"
}
bond = parseInstrument(bond1)
bondFut1 = {
    "productType": "Futures",
    "futuresType": "BondFutures",
    "instrumentId": "T2509",
    "nominal": 100.0,
    "maturity": "2025.09.12",
    "settlement": "2025.09.16",
    "underlying": bond1,
    "nominalCouponRate": 0.03
}
bondFut = parseInstrument(bondFut1)
irs1 =  {
    "productType": "Swap",
    "swapType": "IrSwap",
    "irSwapType": "IrFixedFloatingSwap",
    "start": 2025.06.16,
    "maturity": 2028.06.16,
    "frequency": "Quarterly",
    "fixedRate": 0.018,
    "calendar": "CFET", 
    "fixedDayCountConvention": "Actual365",
    "floatingDayCountConvention": "Actual365",
    "payReceive": "Pay",
    "iborIndex": "FR_007",
    "spread": 0.0001,
    "notionalAmount":1E8,
    "notionalCurrency": "CNY"
}
irs = parseInstrument(irs1)
pricingDate = 2025.08.18
curve1 = {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "curveName": "CNY_FR_007",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Continuous",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "dates":[2025.08.21, 2025.08.27, 2025.09.03, 2025.09.10, 2025.09.22, 2025.10.20, 2025.11.20, 
             2026.02.24,2026.05.20, 2026.08.20, 2027.02.22, 2027.08.20, 2028.08.21],
    "values":[1.4759, 1.5331, 1.5697, 1.5239, 1.4996, 1.5144, 1.5209, 
              1.5539, 1.5461, 1.5316, 1.5376, 1.5435, 1.5699] / 100.0
}
curveCnyFr007 = parseMktData(curve1)
bondCurve =  {
    "mktDataType": "Curve",
    "curveType": "IrYieldCurve",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "curveName": "CNY_TREASURY_BOND",
    "dayCountConvention": "ActualActualISDA",
    "compounding": "Compounded",
    "interpMethod": "Linear",
    "extrapMethod": "Flat",
    "frequency": "Annual",
    "dates":[2025.09.18, 2025.11.18, 2026.02.18, 2026.08.18, 2027.08.18, 2028.08.18, 2030.08.18,
             2032.08.18, 2035.08.18, 2040.08.18, 2045.08.18, 2055.08.18,2065.08.18, 2075.08.18],
    "values":[1.3000, 1.3700, 1.3898, 1.3865, 1.4299, 1.4471, 1.6401,
              1.7654, 1.7966, 1.9930, 2.1834, 2.1397, 2.1987, 2.2225] / 100.0
}
curveCnyTreasuryBond = parseMktData(bondCurve)
fr007HistCurve = {
    "mktDataType": "Curve",
    "curveType": "AssetPriceCurve",
    "curveName": "PRICE_FR_007",
    "referenceDate": pricingDate,
    "currency": "CNY",
    "dates":[2025.05.09, 2025.05.12, 2025.05.13, 2025.05.14, 2025.05.15, 2025.05.16, 2025.05.19, 2025.05.20, 2025.05.21, 2025.05.22,
             2025.05.23, 2025.05.26, 2025.05.27, 2025.05.28, 2025.05.29, 2025.05.30, 2025.06.03, 2025.06.04, 2025.06.05, 2025.06.06,
             2025.06.09, 2025.06.10, 2025.06.11, 2025.06.12, 2025.06.13, 2025.06.16, 2025.06.17, 2025.06.18, 2025.06.19, 2025.06.20,
             2025.06.23, 2025.06.24, 2025.06.25, 2025.06.26, 2025.06.27, 2025.06.30, 2025.07.01, 2025.07.02, 2025.07.03, 2025.07.04,
             2025.07.07, 2025.07.08, 2025.07.09, 2025.07.10, 2025.07.11, 2025.07.14, 2025.07.15, 2025.07.16, 2025.07.17, 2025.07.18,
             2025.07.21, 2025.07.22, 2025.07.23, 2025.07.24, 2025.07.25, 2025.07.28, 2025.07.29, 2025.07.30, 2025.07.31, 2025.08.01,
             2025.08.04, 2025.08.05, 2025.08.06, 2025.08.07, 2025.08.08, 2025.08.11, 2025.08.12, 2025.08.13, 2025.08.14, 2025.08.15
       ],
    "values":[1.6000, 1.5600, 1.5300, 1.5500, 1.5500, 1.6300, 1.6500, 1.6000, 1.5900, 1.5800, 
              1.6300, 1.7000, 1.7000, 1.7000, 1.7500, 1.7500, 1.5900, 1.5800, 1.5700, 1.5600, 
              1.5500, 1.5500, 1.5600, 1.5900, 1.5900, 1.5700, 1.5500, 1.5600, 1.5679, 1.6000, 
              1.5700, 1.8500, 1.8300, 1.8400, 1.8500, 1.9500, 1.6036, 1.5800, 1.5200, 1.5000, 
              1.5000, 1.5100, 1.5100, 1.5300, 1.5200, 1.5500, 1.6000, 1.5400, 1.5400, 1.5000, 
              1.5000, 1.4800, 1.5000, 1.6000, 1.7500, 1.6400, 1.6200, 1.6300, 1.6000, 1.5000, 
              1.4800, 1.4700, 1.4800, 1.4900, 1.4600, 1.4600, 1.4600, 1.4800, 1.4800, 1.4900  
               ]\100
}
priceCurveFr007 = parseMktData(fr007HistCurve)
instrument = [bond, bondFut, irs]
mktData= [curveCnyFr007, curveCnyTreasuryBond, priceCurveFr007]
results = instrumentPricer(instrument, pricingDate, mktData)
print(results)
/*
[99.600846811350891,107.77642440859519,-651143.525606005452573]
*/
```

更多交易类型的例子见
[instrumentPricer](../funcs/i/instrumentPricer.html)
中的例子，也可以参考
[instrumentPricer.dos](script/pricing_functions/instrumentPricer.dos)
。

**（2）VaR 计算**

VaR（风险价值）计算是金融风险管理中的重要工具，主要用于评估在一定置信度下，特定时间内可能遭受的最大损失。通常采用历史模拟法计算 VaR，模拟历史
250 或者 500 个场景。这种计算密集型任务就可以使用
`instrumentPricer`。下面给一个例子的**伪代码**：

```dolphindb
/*
 目标：计算一万只国债的 VaR, 采用历史模拟法构建 500 个场景，置信区间为 99%
 database:
   Instrument: 金融工具表, 保存所有债券的基础信息, 其中的 instrument 字段为 INSTRUMENT 类型
   MarketData：市场数据表，保存定价需要用到的曲线/曲面数据，其中的 data 字段为 MKTDATA 类型       
 计算日：2025.08.18
*/
// Step1：计算参考日的估值，计为 P0
pricingDate = 2025.08.18
curve0 = select data from MarketData where date = pricingDate and name = "CNY_TREASURY_BOND"
P0 = select instrumentPricer(t1.instrument, pricingDate, [curve0]) from Instrument as t1 where t1.subType = "TREASURY_BOND" limit 10000;
nextBusiDate = temporalAdd(pricingDate, 1d, "CFET") // CFET 为中国外汇交易中心交易日历
// Step2：计算情景的估值，第一个情景计为 P1
// 假设第一个历史情景是 2023.08.18 到 2023.08.19 的曲线变化
curve11 = select extraMktData(data) from MarketData where date = 2023.08.18 and name = "CNY_TREASURY_BOND"
curve12 = select extraMktData(data) from MarketData where date = 2023.08.19 and name = "CNY_TREASURY_BOND"
curve1 = extraMktData(curve0)
curve1["referenceDate"] = nextBusiDate
curve1["values"] += curve12["values"] - curve11["values"] 
curve1["dates"] = temporalAdd(curve1["dates"], 1d, "CFET")
curve = parseMktData(curve1)
P1 = select instrumentPricer(t1.instrument, nextBusiDate, [curve]) from Instrument as t1 where t1.subType = "TREASURY_BOND" limit 10000;
// 同P1的计算过程，可以求出P2,P3,...,P500
// Step3：计算 VaR
pnls = [P1, P2,...,P500] - take(P0, 500)
// 取每个合约左侧 99% 值，即可得到 VaR
valueAtRisk = percentile(pnls, 1)
```

### 3.2 portfolioPricer

[portfolioPricer](../funcs/p/portfolioPricer.html)
可以对一个投资组合进行定价。不同于
[instrumentPricer](../funcs/i/instrumentPricer.html)
，其参数中多了一个 amount，可以输入 instrument 中各个元素的头寸（合约数量，可正可负），得到的结果是整个投资组合的 npv。

例子见
[portfolioPricer](../funcs/p/portfolioPricer.html)
中的示例 。

## 4. 总结和展望

此教程对基于 INSTRUMENT 类型金融工具的定价函数做了简要介绍，包括定价原理和示例。目前只推出了部分线性产品定价函数和基于 BlackScholes 公式的外汇欧式期权定价函数。

后续我们会从以下几个方面不断扩充定价函数库：

- 资产类别。目前只支持固收和外汇，后续我们会扩充到大宗商品、权益、加密货币等。
- 衍生品类型。不仅支持场内的欧式期权和美式期权，也支持更多的场外期权和结构化产品。
- 定价模型。目前仅支持 BlackScholes 模型，后续会增加局部波动率模型（Dupire）、随机波动率模型（Heston）、利率模型（Hull-White）等。
- 定价方法。目前仅支持解析解（Analytic），后续会增加有限差分法(PDE) 和 蒙特卡洛法（MonteCarlo） 等方法。
- 风险计量。除了计算期权基本的 Greeks（Delta/Gamma/Vega 等），还可以精细到满足巴塞尔Ⅲ的程度，如 Bucked Delta / Bucked Vega 。

敬请期待！

## 参考

[1] 中国期货业协会. 国债期货[M]. 北京: 中国财政经济出版社, 2013.

[2] 中国外汇交易中心. 产品指引（外汇市场）V4.2：Product Guide (FX Market)[EB/OL]. 上海：中国外汇交易中心，2023: 1-110 [2023-10]
