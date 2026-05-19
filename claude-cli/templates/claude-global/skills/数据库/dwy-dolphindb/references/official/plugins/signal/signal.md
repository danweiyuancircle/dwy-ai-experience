---
source_url: https://docs.dolphindb.cn/zh/plugins/signal/signal.html
fetched_at: 2026-05-19T09:46:37Z
category: plugins
title: signal
sha1: c7e53d1f27ce6477f442bda91fb5dc549f59d4c0
---

# signal

signal 插件集成了功能强大且性能高的 FFTW3 开源傅里叶变换库，为用户提供了便捷高效的傅里叶变换计算方式。该插件包含多种信号处理函数，如离散正弦变换、离散余弦变换和离散小波变换等。用户可以在DolphinDB 中加载该插件并使用这些信号处理功能。

## 安装插件

### 版本要求

DolphinDB Server 2.00.10 及更高版本。

支持 Linux x86、Linux ARM。

### 安装步骤

1. 在 DolphinDB 客户端中使用 `listRemotePlugins` 命令查看插件仓库中的插件信息。

注意：仅展示当前操作系统和 server 版本支持的插件。若无预期插件，可[自行编译](https://gitee.com/dolphindb/DolphinDBPlugin)（请选择对应分支下的插件）或在 [DolphinDB 用户社区](https://ask.dolphindb.cn/)进行反馈。

```dolphindb
login("admin", "123456")
listRemotePlugins()
```

1. 使用 `installPlugin` 命令完成插件安装。

```dolphindb
installPlugin("signal")
```

1. 使用 `loadPlugin` 命令加载插件。

```dolphindb
loadPlugin("signal")
```

## 接口说明

### angle

**语法**

```dolphindb
signal::angle(X, [deg=false])
```

**详情**

返回复数 X 的角度。

**参数**

**X** COMPLEX 类型标量/矩阵/向量。

**deg** 可选参数，BOOL 类型标量。默认值为 false，表示以弧度为单位返回角度，范围为 (-pi, pi]；若设置为 true，则以度为单位返回角度，范围为 (-180, 180]。

### dct

**语法**

```dolphindb
signal::dct(X)
```

**详情**

对离散信号作离散余弦变换，并返回变换后的与输入向量等长的 DOUBLE 类型序列。

**参数**

**X** INT 或 DOUBLE 类型向量，表示输入的离散信号序列。

### dst

**语法**

```dolphindb
signal::dst(X)
```

**详情**

对离散信号作离散正弦变换，并返回变换后的与输入向量等长的 DOUBLE 类型序列。

**参数**

**X** INT 或 DOUBLE 类型向量，表示输入的离散信号序列。

### dwt

**语法**

```dolphindb
signal::dwt(X, [wavelet])
```

**详情**

对离散信号进行一维离散小波变换。返回由变换序列组成的 table，包含两个字段：cA，cD。cA 对应变换后的近似部分序列，cD 对应变换后的细节部分序列。

**参数**

**X** INT 或 DOUBLE 类型向量，表示输入的离散信号序列。

**wavelet** 可选参数，字符串标量，表示小波基函数名称。可指定为 "db1"（默认）或 "db4"。

### dwtEx

**语法**

```dolphindb
signal::dwtEx(X, [wavelet], [level])
```

**详情**

对离散信号进行多层一维离散小波变换，返回一个元组：[cA\_n, cD\_n, cD\_n-1, …, cD2, cD1]。该元组的每个元素都是一个向量，n表示分解的级别。cA\_n 对应变换后的近似部分序列，cD\_n - cD\_n-1 对应变换后的细节部分序列。

**参数**

**X** 浮点或整型向量，表示输入的离散信号序列。

**wavelet** 可选参数，字符串标量，表示小波基函数名称。可指定为 “db1”（默认）, “db2”,.., “db15”。

**level** 可选参数，1到100之间的整数，表示分解层数。默认值为1。

### idwt

**语法**

```dolphindb
signal::idwt(X,Y)
```

**详情**

对一维离散小波变换得到的两个序列进行逆变换，返回得到的信号序列。

**参数**

**X** INT 或 DOUBLE 类型向量，表示输入的近似部分序列（cA）。

**Y** INT 或 DOUBLE 类型向量，表示输入的细节部分序列（cD）。

### dctParallel

**语法**

```dolphindb
signal::dctParallel(ds)
```

**详情**

离散余弦变换的分布式版本，对离散信号作离散余弦变换，返回变换序列。由于 `dctParallel` 函数多用于多线程并发计算，为避免系统负载过高而严重影响性能，请勿多线程使用该函数。

**参数**

**ds** 数据源元组，表示输入的离散信号序列。*ds* 可以由 `sqlDS` 函数返回，包含若干个分区，分布在若干个控制节点中。

### fft

**语法**

```dolphindb
signal::fft(X,[n],[norm])
```

**详情**

一维快速傅立叶变换，返回变换后长度为 *n* 的复数向量。

**参数**

**X** 实数或复数类型向量，表示要进行傅立叶变换的数据。

**n** INT类型标量，表示傅立叶变换后输出向量的长度，默认为 *X* 的长度。

**norm** STRING 类型标量，表示标准化模式，可取以下值：

- "backward"（默认值）：不做标准化。
- "forward"：将变换结果乘以 1/n。
- "ortho"：将变换结果乘以 1/sqrt(n)。

### fft!

**语法**

```dolphindb
signal::fft!(X,[n],[norm])
```

**详情**

一维快速傅立叶变换，计算结果覆盖 *X* 中原元素。注意，仅当 *X* 为复数且长度不小于 *n* 时，前 *n* 项被输出覆盖。

**参数**

与 `fft` 接口相同。

### ifft

**语法**

```dolphindb
signal::ifft(X,[n],[norm])
```

**详情**

一维快速傅立叶逆变换，返回变换后长度为 *n* 的复数向量

**参数**

**X** 实数或复数类型向量，表示要进行傅立叶变换的数据。

**n** INT类型标量，表示傅立叶变换后输出向量的长度，默认为 *X* 的长度。

**norm** STRING 类型标量，表示标准化模式。可取以下值：

- "backward"（默认值）：将变换结果乘以 1/n。
- "forward"：不做标准化。
- "ortho"：将变换结果乘以 1/sqrt(n)。

### ifft!

**语法**

```dolphindb
signal::ifft!(X,[n],[norm])
```

**详情**

一维快速傅立叶逆变换，计算结果覆盖 *X* 中原元素。注意，仅当 *X* 为复数且 *X* 长度不小于 *n* 时，前 *n* 项被输出覆盖。

**参数**

与 `ifft` 接口相同。

### fft2

**语法**

```dolphindb
signal::fft2(X,[s],[norm])
```

**详情**

二维快速傅立叶变换，返回变换后的复数矩阵。

**参数**

**X** 实数或复数类型矩阵，表示要进行傅立叶变换的数据。

**s** 含有两个正整数的向量，分别表示对应傅立叶变换后输出矩阵的行数和列数，默认为 *X* 的行数和列数。

**norm** STRING 类型标量，表示标准化模式，可取以下值（设 n 为矩阵中元素的个数）：

- "backward"（默认值）：不做标准化。
- "forward"：将变换结果乘以 1/n。
- "ortho"：将变换结果乘以 1/sqrt(n)。

### fft2!

**语法**

```dolphindb
signal::fft2!(X,[s],[norm])
```

**详情**

二维快速傅立叶变换，计算结果覆盖 *X* 中原元素。注意仅当 *X* 为复数矩阵且行列数均不小于 *s* 时，被输出覆盖。

**参数**

与 `fft2` 接口相同。

### ifft2

**语法**

```dolphindb
signal::ifft2(X,[s],[norm])
```

**详情**

二维快速傅立叶逆变换，返回变换后的复数矩阵。

**参数**

**X** 实数或复数类型矩阵，表示要进行傅立叶变换的数据。

**s** 含有两个正整数的向量，分别表示对应傅立叶变换后输出矩阵的行数和列数，默认为 *X* 的行数和列数。

**norm** STRING 类型标量，表示标准化模式。可取以下值（设 n 为矩阵中元素的个数）：

- "backward"（默认值）：将变换结果乘以 1/n。
- "forward" ：不做标准化。
- "ortho"：将变换结果乘以 1/sqrt(n)。

### ifft2!

**语法**

```dolphindb
signal::ifft2!(X,[s],[norm])
```

**详情**

二维快速傅立叶逆变换，计算结果覆盖 *X* 中原元素。注意仅当 *X* 为复数矩阵且行列数均不小于 *s* 时，被输出覆盖。

**参数**

与 `ifft2` 接口相同。

### secc

**语法**

```dolphindb
signal::secc(data,template,k,[moveout],[weight])
```

**详情**

波形互相关，返回含有 n 列的矩阵，每列长为 l-m+1，对应 *template* 的第 n 列与 data 互相关的结果。

**参数**

**data** 长度为 l 的一维实数向量，表示波形数据。

**template** n 列m 行的实数矩阵，表示含有 n 段长为 m 的波形数据，每段数据存为矩阵中的一列，且 l 不小于m。

**k** INT 类型标量。k 不小于 2\*m，建议为 2 的幂次方。

**moveout** 长度为 n 的 DOUBLE 类型向量，表示时差，默认全为 0。

**weight** 长度为 n 的 DOUBLE 类型向量，表示权重，默认全为 1。

### abs

**语法**

```dolphindb
signal::abs(data)
```

**详情**

对复数进行求模。如果 *data* 为复数标量，返回 DOUBLE 类型的标量。如果 *data* 为复数的向量，返回 DOUBLE 类型的向量。

**参数**

**data** 复数标量或向量，表示需要进行求模的数据。

### mul

**语法**

```dolphindb
signal::mul(data, num)
```

**详情**

对复数进行乘法运算。返回计算结果，结果形式与 *data* 相同。

**参数**

**data** 复数的标量或向量，表示需要进行乘法的数据。

**num** DOUBLE 类型标量，表示乘数。

# 3. 示例

在运行以下示例前，请先按照前文的“安装插件”步骤，完成 signal 插件的安装和加载。

**例1 dct 离散余弦变换**

```dolphindb
X = [1,2,3,4]
signal::dct(X)
// output: [5,-2.23044235292127,-2.411540739456585E-7,-0.15851240125353]
```

**例2 dst 离散正弦变换**

```dolphindb
X = [1,2,3,4]
signal::dst(X)
// output: [15.388417979126893,-6.88190937668141,3.632712081813623,-1.624597646358306]
```

**例3 dwt 离散小波变换**

```dolphindb
X = [1,2,3]
signal::dwt(X)
// output：
cA                cD                
----------------- ------------------
2.121320343559643 -0.707106781186548
4.949747468305834 -0.707106781186548
```

**例4 idwt 反离散小波变换**

```dolphindb
X = [2.121320343559643,4.949747468305834]
Y = [-0.707106781186548,-0.707106781186548]
signal::dwt(x,y)
// output: [1,2,3.000000000000001,4.000000000000001]
```

**例5 dctParallel 离散余弦变换分布式版本**

```dolphindb
f1=0..9999
f2=1..10000
t=table(f1,f2)
db = database("dfs://rangedb_data", RANGE, 0 5000 10000)
signaldata = db.createPartitionedTable(t, "signaldata", "f1")
signaldata.append!(t)
signaldata=loadTable(db,"signaldata")
ds=sqlDS(<select * from signaldata >)
signal::dctParallel(ds);
```

**例6 fft 一维快速傅立叶变换**

```dolphindb
X = [1,2,3,4]
signal::fft(X);
// output: [10+0i,-2+2i,-2+0i,-2-2i]
```

**例7 ifft 一维快速傅立叶逆变换**

```dolphindb
X = [1,2,3,4]
signal::ifft(X);
// output: [2.5+0i,-0.5-0.5i,-0.5+0i,-0.5+0.5i]
```

**例8 fft2 二维快速傅立叶变换**

```dolphindb
X = matrix([1,2,3,4],[4,3,2,1])
signal::fft2(X);
// output: 
#0    #1   
----- -----
20+0i 0+0i 
0+0i  -4+4i
0+0i  -4+0i
0+0i  -4-4i
```

**例9 fft2 二维快速傅立叶逆变换**

```dolphindb
X = matrix([1,2,3,4],[4,3,2,1])
signal::ifft2(X);
// output: 
#0     #1       
------ ---------
2.5+0i 0+0i     
0+0i   -0.5-0.5i
0+0i   -0.5+0i  
0+0i   -0.5+0.5i
```

**例10 secc 波形互相关**

```dolphindb
x=[1, 2, 1, -1, 0, 3];
y=matrix([1,3,2],[4,1,5]);
signal::secc(x,y,4);
// output: 
#0                 #1               
------------------ -----------------
0.981980506061966  0.692934867183583
0.327326835353989  0.251976315339485
-0.377964473009227 0.327326835353989
0.422577127364258  0.536745040121693
```
