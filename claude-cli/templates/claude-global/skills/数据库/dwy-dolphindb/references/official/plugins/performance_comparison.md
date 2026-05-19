---
source_url: https://docs.dolphindb.cn/zh/plugins/performance_comparison.html
fetched_at: 2026-05-19T09:47:10Z
category: plugins
title: DolphinDB 回测平台与其它回测产品的对比分析
sha1: 39ac7982f9b862bd6dcebee385016ccc278e411a
---

# DolphinDB 回测平台与其它回测产品的对比分析

## DolphinDB 回测平台介绍

DolphinDB 回测框架建立在已有的数据库基础上，以插件的形式提供多种资产回测方案。 DolphinDB
回测框架内嵌有多种资产的回测引擎，对不同的资产框架设置有独立的风险控制系统、模拟撮合引擎，以达到接近实盘交易的回测效果。用户在使用 DolphinDB
回测框架时，无需大规模手动开发模拟实盘交易环境，便可直接本地调用各类引擎，专注于策略开发。依托现有数据库，大规模数据可以减少 I/O
操作，从而以更高效的方式完成回测，进一步降低内存读取的时间损耗，显著缩短回测时间。此外， DolphinDB Backtest
内嵌流数据状态引擎，优化一系列滑动窗口函数，使得整体性能更优。在 JIT 技术的加持下，插件回测的速度还将进一步提高，使脚本语言的执行效率逼近编译语言。

本文比较了 DolphinDB
回测引擎与市面上流行的回测产品在性能和功能方面的差异。实验将采用相同数据和策略，通过控制变量法，仅在不同平台上使用不同的本地语言实现策略，并逐一记录运行时间以评估性能。通过性能对比，进一步呈现
DolphinDB 在性能和功能上的市场比较优势。

本文采用的案例都来自于各个第三方平台自有的经典测试案例。这些案例可以代表各个第三方平台的实际使用场景和性能表现。这些案例的测试结果不构成第三方平台的全部性能体现，但可以从多个角度反映
DolphinDB 与三方量化回测平台的性能差异。

本文所用的 DolphinDB 测试环境配置为：

| **测试环境配置** | |
| --- | --- |
| **OS** | Debian GNU/Linux 12 |
| **Database** | 3.00.2.1 2024.11.04 LINUX\_JIT x86\_64 |
| **CPU** | Intel(R) Xeon(R) Gold 5220R CPU @ 2.20GHz |
| **Memory** | 700G |

以下所有测试均基于单线程计算。

## DolphinDB vs Backtrader

本节主要从 Backtrader 的主要功能特点和相关策略性能上与 DolphinDB 进行对比说明。

### 功能比对

Backtrader 是一个广泛使用的 Python 开源量化交易框架，主要用于算法交易和量化策略回测。该回测框架是事件型交易架构，适用于中低频策略的回测，不支持
tick 级别的回测。Backtrader 的主要特点包括支持期货等衍生品的保证金制度，内置约 122 种指标（如简单移动平均线 SMA、指数移动平均线
EMA、MACD、Stochastic、RSI 等），并集成了 ta-lib 库。在指标计算上，Backtrader
在数据预加载时预先完成回测周期内所有策略指标的向量化计算，从而实现批量计算。原生版本不支持 A 股市场的动态分红除权处理。

DolphinDB
策略回测引擎不仅支持中低频策略回测，还支持逐笔高精度回测，也支持保证金制度，支持A股市场的分红除权以及两融融券等功能的策略回测。此外，DolphinDB
支持多种指标计算，包括 ta、mytt、alpha101 和国泰君安191 指标库，及其他复杂的 m 系列、tm 系列和 cum
系列等自定义指标，使其在回测功能上更为全面。

### 性能比对

下面我们基于 MACD 和 RSI 双重指标作为开仓信号的股票 CTA 策略实现进行性能比对。

**策略介绍**

基于 MACD 和 RSI 双重指标作为开仓信号的股票 CTA
策略。核心逻辑为：利用分钟频数据，计算两个指标变化（MACD、RSI），并设置指标的阈值，一旦越过阈值，触发买入和卖出操作。下面为具体的策略逻辑 。

- 买入开仓：当 MACD 由负转正时(前一 MACD 为负号，当前 MACD 为正)，给出第一个买入信号；如果 RSI 涨破 30
  脱离超卖区域，认为市场上涨，给出第二个买入信号。当同时接收到两个买入信号时，以当前收盘价提交委托订单买入。
- 卖出开仓：当 MACD 由正转负时(前一 MACD 为正号，当前 MACD 为负)，给出第一个卖出信号；如果 RSI 跌破 70
  脱离超买区域，认为市场开始下跌，给出第二个卖出信号。当同时接收到两个卖出信号时，获取持仓数量，确保有足够持仓可供卖出，然后提交订单，以当前收盘价提交委托订单卖出。

**Backtrader 中该策略实现**

下面是 Backtrader
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
 def next(self):
    if self.order:
        return
    try:
        if not self.position:
                if (self.macd[0] > 0 and self.macd[1] < 0 
                  and self.rsi[0] > 30 and self.rsi[1] < 30 ):  
                    self.order = self.buy()
        else:
                if (self.macd[0] < 0 and self.macd[1] > 0 
                  and self.rsi[0] < 70 and self.rsi[1] > 70 ):
                    self.order = self.sell()
    except:
        pass
```

**DolphinDB 中该策略实现**

下面是 DolphinDB
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
def onBar(mutable context, msg, indicator){
   //...
    for (istock in msg.keys()){
        if(macd > 0 and prevMacd < 0 and rsi > 30 and prersi < 30 ){
            ... // 变量命名和传递
            lastPrice = msg[istock]["close"]
            Backtest::submitOrder(context["engine"], (istock,context["tradeTime"] 
              , 5, lastPrice, 1000, 1),"buy")
        }
        if(macd < 0 and prevMacd > 0 and rsi < 70 and prersi > 70 ){
            ... // 变量命名和传递
            openOrders = Backtest::getOpenOrders(context["engine"], istock, , "close")
			remainQty = sum(nullFill(getOpenQty(openOrders), 0))
            if(pos-remainQty > 0){
                Backtest::submitOrder(context["engine"], (istock,context["tradeTime"]
                   , 5, lastPrice, 1000, 2), "sell")
            }
        }
    }
}
```

**性能对比测试**

下面将通过与 Backtrader 的对比展开 DolphinDB 的性能测试。

以 2021.01.04 至 2021.12.31 一年内的 3 支股票的 175689 条数据为回测样本进行测试，并以与 Backtrader
实现的进行性能对比：

|  | **DolphinDB (JIT)**  **V3.00.2.1** | **DolphinDB (非 JIT)**  **V3.00.2.1** | **Python V3.10.15**  **Backtrader V1.9.78.123** |
| --- | --- | --- | --- |
| **运行时间** | 1.5s | 3.2s | 56.3s |

从测试结果可以看出，DolphinDB 在回测中具有显著的速度优势，主要原因包括：

- Backtrader 在大多数情况下是完全基于 Python 的，相比之下， DolphinDB 的回测框架完全基于 C++
  开发。
- DolphinDB 在数据库内实现，这有效地降低了数据持续传入所产生的时间成本。
- DolphinDB 回测插件引入了响应式状态引擎等增量的指标计算。
- DolphinDB 引入了 JIT，降低了解释代码的时间开销。

## DolphinDB vs MetaTrader4

本节主要从 MetaTrader4 的主要功能特点和相关策略性能上与 DolphinDB 进行对比说明。

### 功能比对

MetaTrader4 是一款外汇交易平台，提供实时货币对报价、图表分析、自动化交易支持及策略回测。MetaTrader4 使用 MQL4
作为回测编程语言，该语言是 C 语言的子集，属于编译型语言，相比 Python 等解释型语言执行速度更快。MetaTrader4
支持快照级别的策略回测，但订单不支持高精度的模拟撮合。其指标计算基于 1 分钟、5 分钟、15 分钟、30 分钟、1 小时、4 小时和日等七种固定周期，内置了
20 种常见指标（如移动平均线 MA、相对强弱指数 RSI、布林带和 MACD 等），并支持自定义指标的实现。然而，MQL4
开发自定义指标对策略研究员的编码能力要求较高。

DolphinDB 策略回测引擎不仅支持逐笔高精度回测，还支持高精度的订单撮合，订单成交结果充分考虑市场流动性等因素。DolphinDB
支持全面的指标计算，内置大量 m 系列、tm 系列和 cum 系列函数，使复杂指标的实现更为便捷。

### 性能比对

下面我们基于快照行情，实现布林带突破和 RSI 作为开仓信号的外汇 CTA 趋势策略实现进行性能比对。

**策略介绍**

本策略为外汇交易的布林带突破与 RSI 交易信号策略。该策略以每小时进行指标计算，实时进行风险监控进行止盈止损，下面为具体的策略逻辑：

- 做多开仓：当前 RSI 大于 70 且布林带正在上移并打破上轨
- 做空开仓：当前 RSI 小于 30 且布林带正在下移并打破下轨

如果存在多头或空头委托订单，需根据快照行情判断是否撤单、止盈止损。

**MetaTrader4 实现**

下面是 MetaTrader4
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
void OnTick(){
    //...
   double rsi1 = iRSI(NULL, 0, 11, PRICE_CLOSE, 1);
   double bandsUpper1 = iBands(NULL, 0, 20, 2, 0, PRICE_CLOSE, MODE_UPPER, 1);
   double bandsLower1 = iBands(NULL, 0, 20, 2, 0, PRICE_CLOSE, MODE_LOWER, 1);
   if(buynum ==  0 && rsi1 > 70&& Close[1] > Open[1] && Ask > bandsUpper1){   
      OrderSend(Symbol(), OP_BUY, Lots, Ask, Slippage, Ask-slPoint * Point , 0, 
      "Order Buy",  MagicNum, 0, Blue);
   }
   // rsi 小于 30 ， 上升形态（需要增加） ， 当前价格 打穿下轨
   if(sellnum == 0 && rsi1 < 30&& Open[1] > Close[1] && Bid < bandsLower1){
      OrderSend(Symbol(), OP_SELL, Lots, Bid, Slippage, Bid + slPoint * Point , 0, 
      "Order Sell", MagicNum, 0, Red);  
   }
}
```

**DolphinDB 实现**

下面是 DolphinDB
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
def onBar(mutable context, msg, indicator){ // 主要策略实现函数
	//...
	if(rsi_ > 70. and askPrice0 > bhigh and close > open){
	        if(longpos <1){
				 //... 
	            orderId=Backtest::submitOrder(context["engine"], 
				(istock,symbolSource,
	            context["barTime"], 5, round(askPrice0,5), 
	            askPrice0 - context["sl"] + context['Slippage'],
				askPrice0 + context["tp"] + context['Slippage'], 
	            2, 1, context['Slippage'], 0, 
				context["barTime"]+36000000), "openBuy", 5)
	        	return
    		}
    	}
	if(rsi_ < 30. and bidPrice0 < blow and close < open){
		if(shortpos <1){
			 // ...
		    orderId=Backtest::submitOrder(context["engine"], (istock, symbolSource,
		    context["barTime"], 5, round(bidPrice0,5), 
		    bidPrice0 + context["sl"] - context['Slippage'], 
		    bidPrice0 - context["tp"] - context['Slippage'], 2, 2, 
			context['Slippage'], 0, 
		    context["barTime"] + 36000000), "openSell", 5)
			return
		}
	}
}
```

**性能对比测试：**

下面将通过与外汇交易平台 MT4 的对比展开 DolphinDB 的性能测试。

以外汇 EUR 对 USD 2019.01.02-2023.12.31 共五年的 1.43 亿行数据和1872 笔委托成交订单为数据集，以下是
MetaTrader 4 和 DolphinDB Backtest 的回测耗时：

|  | **DolphinDB ( JIT) V3.00.2.1** | **DolphinDB (非 JIT) V3.00.2.1** | **MetaTrader 4** |
| --- | --- | --- | --- |
| **运行时间** | 60s | 75s | 53s |

从运行结果中可以看出，MT4 基于外汇的分钟频回测比 DolphinDB 更快，这是因为 MT4 采用类 C
的编译型语言，并且在模拟成交时启用了更为简单的见价成交模式。DolphinDB 在启用 JIT 后，尽管使用了更为耗时的高精度模拟撮合引擎，性能已经逼近
MT4。

## DolphinDB vs VNPY

本节主要从 VNPY的 CTA 策略回测框架的主要功能特点和相关策略性能上与 DolphinDB 进行对比说明。

### 功能比对

VNPY 是一个量化交易框架，提供了 CTA 策略的回测功能。该回测功能仅支持单标的的 CTA 策略回测，不支持期货等衍生品的实时保证金制度。VNPY 内置共约
40 个指标，包括简单移动平均线 SMA 和指数移动平均线 EMA 等，以及 MACD、 Stochastic 和 RSI 等指标。指标计算支持 1 分钟、1
小时和日周级别的策略实现，但仅限于简单的单标的 CTA 策略回测。

DolphinDB 策略回测引擎是一个支持多标的策略回测的通用策略回测框架，支持中低频策略回测，支持逐笔高精度的策略回测。它支持保证金制度，并支持 A
股市场的分红除权以及两融融券等功能的策略回测。DolphinDB 支持更多指标的计算，包括 ta、mytt、alpha101
和国泰君安191，以及其它自定义的复杂指标，涵盖 DolphinDB 中实现的 m 系列、tm 系列和 cum 系列函数。

### 性能比对

期货市场是 DolphinDB 支持的重要市场，本案例沿用分钟频的期货 CTA 策略作为性能测试的案例，以查看二者在指标计算上的性能差异。

**策略介绍**

基于 ATR （平均真实范围）和 RSI（相对强弱指数）结合的技术分析指标实现期货 CTA 策略。具体的策略逻辑如下：

- 买入开仓：RSI 值大于 70 且 ATR 大于其 10 分钟均值
- 卖出开仓：RSI 值小于 30 且 ATR 大于其 10 分钟均值

止损逻辑：

- 卖平：持有多仓时，K 线达到最高点后，回落 0.004 时
- 买平：持有空仓时，K 线达到最低点后，反弹 0.004 时

**VNPY策略实现**

下面是 VNPY
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
   def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        #...
        atr_array = am.atr(self.atr_length, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()
        self.rsi_value = am.rsi(self.rsi_length)
        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            if self.atr_value > self.atr_ma:
                if self.rsi_value > self.rsi_buy:
                    self.buy(bar.close_price + 5, self.fixed_size)
                elif self.rsi_value < self.rsi_sell:
                    self.short(bar.close_price - 5, self.fixed_size)
        if (self.pos > 0) &(bar.high_price > self.intra_trade_high):
             self.intra_trade_high = bar.high_price
        elif (self.pos > 0)  & 
          (bar.close_price < self.intra_trade_high*(1 - self.closeLine)):
            self.sell(bar.close_price, abs(self.pos), stop = True)
        if (self.pos < 0) &(bar.low_price < self.intra_trade_low):
             self.intra_trade_low = bar.low_price
        elif (self.pos < 0)  & 
          (bar.close_price > self.intra_trade_low*(1 + self.closeLine)):
            self.cover(bar.close_price, abs(self.pos), stop=True)

        #...
```

**DolphinDB 策略实现**

下面是 DolphinDB
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
def onBar(mutable context, msg, indicator){
	keys =msg.keys()
	for(i in keys){
		... // 
		//没有多头持仓，并且多头趋势时，买入
		if(longPos < 1 and shortPos < 1 and atr>matr 
			and rsi > context["buySignalRSI"] and matr > 0){
			Backtest::submitOrder(context["engine"], (istock, symbolSource,
			context["tradeTime"], 5, price + 0.02, 0., 2, 1, 0), "buyOpen")
		        	highDict[istock] = price
		        	continue
		}
		//没有空头持仓，并且空头趋势时，卖出
		if(longPos < 1 and shortPos < 1 and atr > matr 
			and rsi < context["sellSignalRSI"] and matr > 0){
			Backtest::submitOrder(context["engine"], ( istock,
				symbolSource,context["tradeTime"], 5, price-0.02, 0., 2, 2, 0), 
				"sellOpen")
		    lowDict[istock] = price
		    continue
		}
		if(longPos > 0 and price > highDict[istock]){//更新最高价
		        	highDict[istock] = max(price, highDict[istock])
		} 
		else if(longPos > 0  
			and price <= highDict[istock]*(1 - context["closeLine"])){
		//平仓
			Backtest::submitOrder(context["engine"], (istock, symbolSource,
				context["tradeTime"], 5, price - 0.02, 0., 2, 3, 0), "sellClose")
		}
		if(shortPos > 0 and price < lowDict[istock]){//更新最低价
		        	lowDict[istock] = min(price, lowDict[istock])
		} 
		else if(shortPos > 0  
			and price >= lowDict[istock]*(1 + context["closeLine"])){
		//平仓
			Backtest::submitOrder(context["engine"], (istock, symbolSource, 
				context["tradeTime"], 5, price + 0.02, 0., 2, 4, 0), "buyClose")
		}		
	}
}
```

下面将通过与一个开源量化交易框架 VNPY 的对比展开 DolphinDB 的性能测试。

**性能对比测试**

VNPY 是一个基于 Python 的开源量化交易框架，支持回测、模拟交易、实时交易等各种模式。接下来，将以 VNPY 为基准，展开 DolphinDB 与
VNPY 的对比测试。

下面以 1 个月 ’AG2306‘ 期货主力连续合约分钟行情共 2 万条数据量为回测样本，进行 DolphinDB 回测框架与 VNPY 的性能对比：

|  | **DolphinDB ( JIT) V3.00.2.1** | **DolphinDB (非 JIT) V3.00.2.1** | **VNPY V3.0** |
| --- | --- | --- | --- |
| **运行时间** | 0.2s | 0.5s | 4.1s |

对于小样本量， DolphinDB 仍然有显著的性能优势，这是因为 Backtest
能够调用数据库的一系列功能，在数据库环境下完成回测，从而降低回测系统的复杂度。这里仅回测了一支标的，是因为
VNPY仅支持单支标的回测，需要保持实验条件一致。

## DolphinDB vs 功夫量化

本节主要从功夫量化的主要功能特点和相关策略性能上与 DolphinDB 进行对比说明。

### 功能比对

功夫量化是一款内核基于 C++ 开发的量化交易平台，支持实时交易、模拟交易及实盘交易，能够提供基于Python
编写的股票、期货、外汇等多种类策略回测。该平台支持国内 A 股市场的 level-2 逐笔成交行情的高精度订单模拟撮合，支持逐笔策略回测。功夫量化允许使用原生
Python 定义高频因子的指标计算。

DolphinDB 策略回测引擎支持沪深 Level-2 行情的逐笔高精度策略回测，支持股票、期货、外汇和银行间债券等多种金融市场的策略回测。回测引擎框架完全使用
C++ 开发，同时编写回测的脚本语言支持使用 JIT 技术来提升策略执行效率。

### 性能比对

通过分析当前的买卖单数量形成下单信号是订单簿不平衡策略的核心逻辑，这对于量化平台的订单实时更新提出了较高的要求。因此，我们选择股票订单簿不平衡策略作为性能测试脚本，以测试
DolphinDB 和功夫量化的订单更新和快照级数据处理能力。

**策略介绍**

本策略是基于市场深度和成交量变化作为开仓信号的股票交易策略。利用实时行情数据，分析买卖双方的成交量的比值关系，并设置对应的阈值，一旦突破该阈值，触发买入和卖出操作。在行情快照数据中，同时计算买方和卖方的成交量，以及相应的持仓情况。下面为具体的策略逻辑：

- 买入开仓：当买方的成交量高于卖方成交量的两倍且卖方成交量大于零时，给出买入信号；获取当前持仓数量，如果持仓数量不超出最大值，并以当前的最佳卖价提交买单。
- 卖出开仓：当卖方的成交量高于买方成交量的两倍且买方成交量大于零时，给出卖出信号；获取当前持仓数量，确保有足够的仓位可供卖出，然后以当前最佳买价提交卖出委托订单。

**功夫量化策略实现**

下面是功夫量化的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
# 快照数据回调
def on_quote(context, quote, location, dest):
    #...
    # 策略逻辑
    ask_volume_sum = sum(x for x in quote.ask_volume)
    bid_volume_sum = sum(x for x in quote.bid_volume)
    if bid_volume_sum > 2 * ask_volume_sum and ask_volume_sum > 0:
        position = get_position(quote.instrument_id, context.book) 
        if not position or position.volume < MAX_POSITION:
            order_id = context.insert_order(quote.instrument_id, 
              quote.exchange_id, source, account, quote.ask_price[0], ORDER_VOLUME,
              PriceType.Limit, Side.Buy, Offset.Open)
    if ask_volume_sum > 2 * bid_volume_sum and bid_volume_sum > 0:
        position = get_position(quote.instrument_id, context.book) 
        if position and position.volume > ORDER_VOLUME:
            order_id = context.insert_order(quote.instrument_id, 
              quote.exchange_id, source, account, quote.bid_price[0], ORDER_VOLUME,
              PriceType.Limit, Side.Sell, Offset.Close)
```

**DolphinDB 实现**

下面是 DolphinDB
的主要策略实现代码，完整实现脚本可见附件：

```dolphindb
def onSnapshot(mutable context, msg, indicator){
	maxP = context["MAX_POSITION"]
	orderV = context["ORDER_VOLUME"]
	istock = msg.symbol
	ask_volume_sum = sum(msg.offerQty)
	bid_volume_sum = sum(msg.bidQty)
	if (ask_volume_sum > 0){
	    if (bid_volume_sum > 2*ask_volume_sum){
	        posL = Backtest::getPosition(context["engine"],istock).longPosition
	        if(posL < maxP){
	            buyPrice = msg.bidPrice[1]
	            Backtest::submitOrder(context["engine"], 
					(istock,context["tradeTime"], 5, buyPrice, orderV, 1),'oimOBUY')	
	        }
	    }
	}
	if (bid_volume_sum > 0){
	    if (2*bid_volume_sum < ask_volume_sum){
	        posH = Backtest::getPosition(context["engine"],istock).shortPosition[0]
	        if(posH >= orderV){
	            sellPrice = msg.offerPrice[1]
	            Backtest::submitOrder(context["engine"],  
					(istock,context["tradeTime"], 5, sellPrice, orderV, 2),'oimOSELL')      	
	        }
	    }
	} 
}
```

**性能对比测试**

下面展示**功夫量化**和 DolphinDB 的性能测试。

使用八支股票一个月的快照共 85 万条行情作为测试数据，通过功夫 Windows 客户端软件云提交到服务器测试功夫量化的运行效率(纯 Python 接口)，并对比
DolphinDB 的性能，得到以下结果：

|  | **DolphinDB（JIT）**  **V3.00.2.1** | **DolphinDB（非JIT）**  **V3.00.2.1** | **功夫量化**  **V2.7.6** |
| --- | --- | --- | --- |
| **运行时间** | 1.1s | 5.7s | 124s |

由于 DolphinDB 数据库带来的数据传输速度提升以及 C++ 框架的加持， DolphinDB 的回测速度相比功夫量化的 Python
接口版本明显更快。

## 小结

在交易性能测试对比之余，下面还添加了功能对比测试的表格，以供参考。

|  | **DolphinDB V3.00.2.1** | **Backtrader V1.9.78.123** | **MetaTrader 4** | **VNPY V3.0** | **功夫量化 V2.7.6** |
| --- | --- | --- | --- | --- | --- |
| **跨品种** | ✔ | ✔ | × | × | ✔ |
| **订单延迟模拟** | ✔ | ×  需在代码中手动模拟延迟 | × | × | ✔ |
| **并行回测** | ✔ | ×  需要利用multiprocessor并行 | ×  需要多个MT4实例 | × | ✔ |
| **按交易所规则模拟撮合** | ✔ | ×  仅支持简单的撮合模型 | × | × | ✔ |
| **手续费** | ✔ | ✔ | ✔ | ✔ | ✔ |
| **实时保证金计算与风控** | ✔ | /  不涉及 | × | × | ✔ |
| **摩擦成本估计** | 综合考虑量价得出，可设置模拟交易比例 | 通过设置滑点估计摩擦成本 | 弱，无法动态模拟 | 通过设置滑点估计摩擦成本 | 通过订单参数模拟到达交易所时间，不支持设置成交比例 |
| **分红** | ✔ | ✔  需要手动设置策略模拟分红 | /  不涉及 | × | ✔ |
| **逐笔回测** | ✔ | × | × | × | ✔ |
| **支持行情预处理生成信号** | ✔ | ✔ | 只支持预处理 | × | × |
| **指标计算** | ✔ | 支持分钟频以上行情的部分指定指标的计算 | ✔  只有20个左右的指标，自定义实现复杂 | 支持分钟频以上行情的20个以下的内置指标的计算 | ✔ |
| **组合策略回测** | ✔ | ✔ | × | × | ✔ |

- 相比 DolphinDB 回测平台，Backtrader
  对于超高频交易的支持较弱；对于订单延迟、复杂的模拟撮合等功能，用户需要在策略中手动实现。此外，Backtrader
  缺乏内置的风险管理功能（如实时保证金计算）。相比之下， DolphinDB 支持更全面，可以通过各种接口获得相应的参数和功能。
- 对比 MT4， DolphinDB
  功能性更全，对并行化回测支持良好。在资产规模较大、资产品种更灵活、以及回测表现对市场流动性更敏感的中高频回测场景中，DolphinDB
  有明显的易用性优势。
- DolphinDB 的风控系统相比 VNPY 有显著的优势：对于期货交易，内嵌的风险控制系统非常重要，如果需要用户从零开发，将付出大量的时间成本。而在使用
  DolphinDB 回测平台时，仅需输入一些形式参数即可； VNPY 仅支持单支标的的回测，DolphinDB
  支持多标的同时回测。另外，DolphinDB 支持逐笔高频回测，而 VNPY 对高频回测的支持有限。
- DolphinDB 相比于功夫量化支持沪深 A 股更高精度的逐笔回测， 在使用脚本编写策略时，支持使用 JIT 技术来提升策略执行效率。

综上所述，DolphinDB 回测框架已经实现了多资产覆盖、模拟回测仿真和风险控制系统。与 Backtrader、VNPY、功夫量化相比， DolphinDB
在回测速度上实现了数量级的飞跃，在功能上更加完善。对比 MT4，DolphinDB 使用 JIT
后，让脚本语言编写的策略逼近编译型语言的性能；在业务功能方面，DolphinDB 对并行回测和高频交易的支持更佳。

## 附录

**测试代码**

**功夫量化 level2行情订单不平衡策略回测**

- 订单不平衡策略 DolphinDB 实现：<data/Kungfu_v.s._DolphinDB.dos>
- 订单不平衡策略 功夫量化 实现：<data/Kungfu_OrderBookImbalance.txt>

**backtrader 股票分钟CTA**

- onBarDemo 策略 DolphinDB 实现：<data/backtrader_v.s._DolphinDB.dos>
- onBarDemo 策略 Python Backtrader 实现：<data/PythonBacktrader_onBarCTA.txt>
- onBarDemo 策略数据：<data/mink_data.csv>

**MT4 RSi+布林带趋势策略**

- RSI + 布林带策略 DolphinDB 实现：<data/MT4_v.s._DolphinDB.dos>
- RSI + 布林带策略 MT4 实现：<data/MT4_BollingBand.mq4>

**VNPY 期货CTA策略**

- 期货 CTA 策略 DolphinDB 实现：<data/VNPY_v.s._DolphinDB.dos>
- 期货 CTA 策略 VNPY 实现：<data/VNPY_CTA.py>
