---
source_url: https://docs.dolphindb.cn/zh/funcs/funcs_by_topics.html
fetched_at: 2026-05-19T09:12:23Z
category: funcs
title: 函数分类
sha1: 1f481cd6d0fdd8a6040c2cd3ec31b97e4b923e65
---

# 函数分类

DolphinDB 的函数按照功能可以分为以下类别：

## 数据操作

- **数据类型与转换：**[array](a/array.html), [arrayVector](a/arrayVector.html),
  [bigarray](b/bigarray.html), [blob](b/blob.html), [bool](b/bool.html), [cast](c/cast.html), [ceil](c/ceil.html),
  [char](c/char.html), [complex](c/complex.html), [date](d/date.html), [datehour](d/datehour.html), [datetime](d/datetime.html), [decimal32](d/decimal32.html), [decimal64](d/decimal64.html), [decimal128](d/decimal128.html), [decimalFormat](d/decimalFormat.html), [decimalMultiply](d/decimalMultiply.html),
  [deg2rad](d/deg2rad.html), [dict](d/dict.html), [double](d/double.html), [duration](d/duration.html), [enlist](e/enlist.html), [fixedLengthArrayVector](f/fixedLengthArrayVector.html),
  [floor](f/floor.html), [float](f/float.html), [form](f/form.html), [format](f/format.html), [fromJson](f/fromJson.html), [fromStdJson](f/fromStdJson.html),
  [hex](h/hex.html), [highDouble](h/highDouble.html), [highLong](h/highlong.html), [indexedSeries](i/indexedSeries.html), [int](i/int.html), [int128](i/int128.html), [ipaddr](i/ipaddr.html), [isColumnarTuple](i/isColumnarTuple.html), [isIndexedMatrix](i/isIndexedMatrix.html), [isIndexedSeries](i/isIndexedSeries.html), [isOrderedDict](i/isOrderedDict.html), [jsonExtract](j/jsonextract.html), [long](l/long.html), [lowDouble](l/lowDouble.html), [lowLong](l/lowlong.html), [makeKey](m/makeKey.html),
  [makeSortedKey](m/makeSortedKey.html), [matrix](m/matrix.html), [minute](m/minute.html), [month](m/month.html), [nanotime](n/nanotime.html), [nanotimestamp](n/nanotimestamp.html), [objectType](o/objectType.html), [pair](p/pair.html), [parseInt](p/parseInt.html), [parseInteger](p/parseInteger.html), [parsejsonTable](p/parsejsontable.html),
  [point](p/point.html), [quarterOfYear](q/quarterOfYear.html), [rad2deg](r/rad2deg.html), [reverse](r/reverse.html), [round](r/round.html), [second](s/second.html), [seq](s/seq.html),
  [set](s/set.html), [setIndexedMatrix!](s/setIndexedMatrix_.html), [setIndexedSeries!](s/setIndexedSeries_.html), [short](s/short.html), [string](s/string.html), [subtuple](s/subtuple.html), [symbol](s/symbol.html), [symbolCode](s/symbolCode.html), [syncDict](s/syncDict.html), [temporalFormat](t/temporalFormat.html), [temporalParse/datetimeParse](t/temporalParse.html), [tensor](t/tensor.html),
  [time](t/time.html), [timestamp](t/timestamp.html), [toJson](t/toJson.html), [toStdJson](t/toStdJson.html), [transpose](t/transpose.html)/[flip](f/flip.html), [type](t/type.html), [typestr](t/typestr.html), [uuid](u/uuid.html)
- **生成：**
  [eye](e/eye.html), [panel](p/panel.html),
  [rollingPanel](r/rollingPanel.html), [seq](s/seq.html), [stretch](s/stretch.html), [take](t/take.html), [til](t/til.html)
- **追加：**[appendEvent](a/appendEvent.html),
  [appendEventWithResponse](a/appendeventwithresponse.html),
  [appendOrcaStreamTable](a/appendOrcaStreamTable.html),
  [append!](a/append!.html)/[push!](p/push_.html), [appendTuple!](a/appendTupel_.html),
  [memberModify!](m/membermodify.html), [peekAppend](p/peekAppend.html)
  [append!](a/append!.html)/[push!](p/push_.html)
- **删除、清理：**[clear!](c/clear_.html), [drop](d/drop.html), [dropna](d/dropna.html), [erase!](e/erase_.html), [pop!](p/pop_.html), [removeHead!](r/removeHead_.html), [removeTail!](r/removeTail_.html),
  [remove!](r/remove.html)
- **查找：**[at](a/at.html), [binsrch](b/binsrch.html), [cell](c/cell.html), [cells](c/cells.html), [col](c/col.html),
  [eachAt(@)](../progr/operators/eachAt.html), [find](f/find.html), [first](f/first.html),
  [firstHit](f/firstHit.html), [firstNot](f/firstNot.html), [head](h/head.html), [ifirstHit](i/ifirstHit.html), [ifirstNot](i/ifirstNot.html), [ilastNot](i/ilastNot.html), [last](l/last.html), [lastNot](l/lastNot.html), [loc](l/loc.html), [milastNot](m/milastNot.html), [row](r/row.html), [searchK](s/searchK.html), [slice](s/slice.html), [sliceByKey](s/sliceByKey.html), [subarray](s/subarray.html), [tail](t/tail.html)
- **排序：**[denseRank](d/denseRank.html), [isort](i/isort.html), [isort!](i/isort_.html), [isortTop](i/isortTop.html), [isSorted](i/isSorted.html), [rank](r/rank.html), [sort](s/sort.html), [sort!](s/sort_.html), [sortBy!](s/sortBy_.html), [rowFilterAndSort](r/rowfilterandsort.html), [rowMergeAndSort](r/rowmergeandsort.html)
- **空值查找、填充：**[bfill](b/bfill.html), [bfill!](b/bfill_.html), [ffill](f/ffill.html), [ffill!](f/ffill_.html), [fill!](f/fill_.html), [hasNull](h/hasNull.html), [ifNull](i/ifNull.html), [ifValid](i/ifValid.html), [interpolate](i/interpolate.html), [isNanInf](i/isNanInf.html), [isNothing](i/isNothing.html), [isNull](i/isNull.html), [isValid](i/isValid.html), [isVoid](i/isVoid.html), [lfill](l/lfill.html), [lfill!](l/lfill_.html), [nanInfFill](n/nanInfFill.html), [nullFill](n/nullFill.html), [nullFill!](n/nullFill_.html)
- **替换：**[replace](r/replace.html), [replace!](r/replace_.html)
- **移动：**[lshift](l/lshift.html), [move](m/move.html), [next](n/next.html), [nextState](n/nextState.html), [prev](p/prev.html), [prevState](p/prevState.html), [rshift](r/rshift.html)
- **合并：**[concatMatrix](c/concatMatrix.html), [join](j/join.html), [join!](j/join!.html), [merge](m/merge.html), [union](u/union.html), [unionAll](u/unionAll.html)
- **分割：**[cut](c/cut.html)
- **过滤：**[conditionalFilter](c/conditionalFilter.html)
- **对齐：**[align](a/align.html)
- **展开、重组：**[flatten](f/flatten.html), [regroup](r/regroup.html), [reshape](r/reshape.html), [shuffle](s/shuffle.html), [shuffle!](s/shuffle_.html), [toArray](t/toArray.html), [toColumnarTuple](t/tocolumnartuple.html), [toTuple](t/totuple.html), [ungroup](u/ungroup.html)
- **分组：**[bar](b/bar.html), [bucket](b/bucket.html), [cutPoints](c/cutPoints.html), [dailyAlignedBar](d/dailyAlignedBar.html), [digitize](d/digitize.html), [groups](g/groups.html),
  [segment](s/segment.html), [volumeBar](v/volumeBar.html)
- **加载：**[loadNpy](l/loadNpy.html), [loadNpz](l/loadNpz.html), [loadRecord](l/loadRecord.html), [loadTable](l/loadTable.html),
  [loadText](l/loadText.html), [loadTextEx](l/loadTextEx.html), [ploadText](p/ploadText.html)
- **编码转换：**[base64Decode](b/base64Decode.html), [base64Encode](b/base64Encode.html), [compress](c/compress.html), [decodeShortGenomeSeq](d/decodeShortGenomeSeq.html),
  [decompress](d/decompress.html), [encodeShortGenomeSeq](e/encodeShortGenomeSeq.html),
  [genShortGenomeSeq](g/genShortGenomeSeq.html),
  [oneHot](o/oneHot.html), [pack](p/pack.html), [rdp](r/rdp.html), [unpack](u/unpack.html)
- **累积窗口：**[cumavg](c/cumavg.html), [cumbeta](c/cumbeta.html), [cumcorr](c/cumcorr.html), [cumcount](c/cumcount.html), [cumcovar](c/cumcovar.html), [cumcovarp](c/cumcovarp.html), [cumfirstNot](c/cumfirstNot.html), [cumlastNot](c/cumlastNot.html), [cummax](c/cummax.html), [cummed](c/cummed.html), [cummin](c/cummin.html), [cumnunique](c/cumnunique.html), [cumpercentile](c/cumpercentile.html), [cumPositiveStreak](c/cumPositiveStreak.html), [cumprod](c/cumprod.html),
  [cumrank](c/cumrank.html), [cumstd](c/cumstd.html), [cumstdp](c/cumstdp.html), [cumsum](c/cumsum.html), [cumsum2](c/cumsum2.html), [cumsum3](c/cumsum3.html), [cumsum4](c/cumsum4.html), [cumvar](c/cumvar.html), [cumvarp](c/cumvarp.html), [cumwavg](c/cumwavg.html), [cumwsum](c/cumwsum.html), [dynamicGroupCumsum](d/dynamicGroupCumsum.html), [dynamicGroupCumcount](d/dynamicGroupCumcount.html)
- **m 系列：**[mavg](m/mavg.html), [mbeta](m/mbeta.html), [mcorr](m/mcorr.html), [mcount](m/mcount.html), [mcovar](m/mcovar.html), [mcovarp](m/mcovarp.html), [mfirst](m/mfirst.html), [mfirstNot](m/mifirstNot.html), [mifirstNot](m/mifirstNot.html),
  [milastNot](m/milastNot.html), [mimax](m/mimax.html), [mimin](m/mimin.html), [mkurtosis](m/mkurtosis.html), [mlast](m/mlast.html), [mlastNot](m/mlastnot.html), [mLowRange](m/mlowrange.html), [mmad](m/mmad.html), [mmax](m/mmax.html),
  [mmaxPositiveStreak](m/mmaxPositiveStreak.html), [mmed](m/mmed.html), [mmin](m/mmin.html),
  [mmse](m/mmse.html), [movingTopNIndex](m/movingTopNIndex.html), [movingWindowData](m/movingWindowData.html), [movingWindowIndex](m/movingWindowIndex.html), [mpercentile](m/mpercentile.html), [mprod](m/mprod.html), [mrank](m/mrank.html), [mskew](m/mskew.html), [mslr](m/mslr.html),
  [mstd](m/mstd.html), [mstdp](m/mstdp.html), [msum](m/msum.html), [msum2](m/msum2.html), [mTopRange](m/mtoprange.html), [mvar](m/mvar.html), [mvarp](m/mvarp.html),
  [mwavg](m/mwavg.html), [mwsum](m/mwsum.html)
- **tm 系列：**[tmavg](t/tmavg.html), [tmbeta](t/tmbeta.html), [tmcorr](t/tmcorr.html), [tmcount](t/tmcount.html), [tmcovar](t/tmcovar.html), [tmcovarp](t/tmcovarp.html), [tmfirst](t/tmfirst.html), [tmkurtosis](t/tmkurtosis.html), [tmlast](t/tmlast.html), [tmLowRange](t/tmlowrange.html), [tmmax](t/tmmax.html), [tmmed](t/tmmed.html), [tmmin](t/tmmin.html), [tmpercentile](t/tmpercentile.html), [tmovingWindowData](t/tmovingWindowData.html), [tmprod](t/tmprod.html), [tmrank](t/tmrank.html), [tmskew](t/tmskew.html), [tmstd](t/tmstd.html), [tmstdp](t/tmstdp.html), [tmsum](t/tmsum.html), [tmsum2](t/tmsum2.html), [tmTopRange](t/tmtoprange.html),
  [tmvar](t/tmvar.html), [tmvarp](t/tmvarp.html), [tmwavg](t/tmwavg.html), [tmwsum](t/tmwsum.html)
- **mTopN：**[cumavgTopN](c/cumavgTopN.html), [cumbetaTopN](c/cumbetaTopN.html), [cumcorrTopN](c/cumcorrTopN.html), [cumcovarTopN](c/cumcovarTopN.html), [cumcovarpTopN](c/cumcovarpTopN.html), [cumkurtosisTopN](c/cumkurtosisTopN.html), [cumskewTopN](c/cumskewTopN.html), [cumstdTopN](c/cumstdTopN.html), [cumstdpTopN](c/cumstdpTopN.html), [cumsumTopN](c/cumsumTopN.html), [cumvarTopN](c/cumvarTopN.html), [cumvarpTopN](c/cumvarpTopN.html), [cumwsumTopN](c/cumwsumTopN.html), [mavgTopN](m/mavgTopN.html), [mbetaTopN](m/mbetaTopN.html), [mcorrTopN](m/mcorrTopN.html), [mcovarTopN](m/mcovarTopN.html), [mcovarpTopN](m/mcovarpTopN.html), [mkurtosisTopN](m/mkurtosisTopN.html), [mpercentileTopN](m/mpercentiletopn.html), [mskewTopN](m/mskewTopN.html), [mstdpTopN](m/mstdpTopN.html), [mstdTopN](m/mstdTopN.html), [msumTopN](m/msumTopN.html), [mvarpTopN](m/mvarpTopN.html), [mvarTopN](m/mvarTopN.html), [mwsumTopN](m/mwsumTopN.html)
- **tmTopN**: [tmavgTopN](t/tmavgTopN.html), [tmbetaTopN](t/tmbetaTopN.html), [tmcorrTopN](t/tmcorrTopN.html), [tmcovarTopN](t/tmcovarTopN.html), [tmcovarpTopN](t/tmcovarpTopN.html), [tmkurtosisTopN](t/tmkurtosisTopN.html), [tmskewTopN](t/tmskewTopN.html), [tmstdTopN](t/tmstdTopN.html), [tmstdpTopN](t/tmstdpTopN.html), [tmsumTopN](t/tmsumTopN.html),
  [tmvarTopN](t/tmvarTopN.html), [tmvarpTopN](t/tmvarpTopN.html), [tmwsumTopN](t/tmwsumTopN.html)
- **row 系列：**[rowAlign](r/rowAlign.html), [rowAnd](r/rowAnd.html),
  [rowAt](r/rowAt.html), [rowAvg](r/rowAvg.html), [rowBeta](r/rowBeta.html), [rowCorr](r/rowCorr.html), [rowCount](r/rowCount.html), [rowCovar](r/rowCovar.html), [rowCovarp](r/rowCovarp.html), [rowCummax](r/rowCummax.html), [rowCummin](r/rowCummin.html), [rowCumprod](r/rowCumprod.html), [rowCumsum](r/rowCumsum.html), [rowCumwsum](r/rowCumwsum.html), [rowDenseRank](r/rowDenseRank.html), [rowDot](r/rowDot.html), [rowEuclidean](r/rowEuclidean.html), [rowGmd5](r/rowgmd5.html), [rowImax](r/rowImax.html),
  [rowImin](r/rowImin.html), [rowKurtosis](r/rowKurtosis.html), [rowMax](r/rowMax.html), [rowMin](r/rowMin.html), [rowMove](r/rowMove.html), [rowNext](r/rowNext.html), [rowOr](r/rowOr.html), [rowPrev](r/rowPrev.html), [rowProd](r/rowProd.html), [rowRank](r/rowRank.html), [rowSize](r/rowSize.html), [rowSkew](r/rowSkew.html), [rowStd](r/rowStd.html), [rowStdp](r/rowStdp.html), [rowSum](r/rowSum.html), [rowSum2](r/rowSum2.html), [rowTanimoto](r/rowTanimoto.html), [rowVar](r/rowVar.html), [rowVarp](r/rowVarp.html), [rowWavg](r/rowWavg.html), [rowWsum](r/rowWsum.html), [rowXor](r/rowXor.html)
- **TA-lib 系列：**[dema](d/dema.html), [ema](e/ema.html), [gema](g/gema.html),
  [kama](k/kama.html), [linearTimeTrend](l/linearTimeTrend.html), [ma](m/ma.html), [sma](s/sma.html), [t3](t/t3.html), [tema](t/tema.html), [trima](t/trima.html), [wilder](w/wilder.html), [wma](w/wma.html)
- **字符串：**[charAt](c/charAt.html), [concat](c/concat.html), [convertEncode](c/convertEncode.html), [crc32](c/crc32.html), [endsWith](e/endsWith.html), [fromUTF8](f/fromUTF8.html), [gmd5](g/gmd5.html), [ilike](i/ilike.html), [initcap](i/initcap.html), [isAlNum](i/isAlNum.html), [isAlpha](i/isAlpha.html), [isDigit](i/isDigit.html), [isLower](i/isLower.html), [isNumeric](i/isNumeric.html), [isSpace](i/isSpace.html), [isTitle](i/isTitle.html), [isUpper](i/isUpper.html), [left](l/left.html), [like](l/like.html), [lower](l/lower.html),
  [lpad](l/lpad.html), [ltrim](l/ltrim.html), [md5](m/md5.html), [regexCount](r/regexCount.html), [regexFind](r/regexFind.html), [regexFindStr](r/regexfindstr.html), [regexReplace](r/regexReplace.html), [repeat](r/repeat.html), [right](r/right.html), [rpad](r/rpad.html), [rtrim](r/rtrim.html), [split](s/split.html), [startsWith](s/startsWith.html), [stringFormat](s/stringFormat.html), [strip](s/strip.html), [strlen](s/strlen.html), [strlenu](s/strlenu.html), [strpos](s/strpos.html), [strReplace](s/strReplace.html), [substr](s/substr.html), [substru](s/substru.html), [toCharArray](t/toCharArray.html), [toUTF8](t/toUTF8.html), [trim](t/trim.html), [upper](u/upper.html)
- **时间处理：**[addMarketHoliday](a/addMarketHoliday.html),
  [asFreq](a/asFreq.html), [businessDay](b/businessDay.html), [businessMonthBegin](b/businessMonthBegin.html), [businessMonthEnd](b/businessMonthEnd.html), [businessQuarterBegin](b/businessQuarterBegin.html), [businessQuarterEnd](b/businessQuarterEnd.html), [businessYearBegin](b/businessYearBegin.html), [businessYearEnd](b/businessYearEnd.html), [concatDateTime](c/concatDateTime.html), [convertTZ](c/convertTZ.html), [date](d/date.html), [dayOfMonth](d/dayOfMonth.html), [dayOfWeek](d/dayOfWeek.html), [dayOfYear](d/dayOfYear.html), [daysInMonth](d/daysInMonth.html),
  [fy5253](f/fy5253.html), [fy5253Quarter](f/fy5253Quarter.html), [getMarketCalendar](g/getMarketCalendar.html), [gmtime](g/gmtime.html), [hour](h/hour.html), [hourOfDay](h/hourOfDay.html), [isLeapYear](i/isLeapYear.html), [isMonthEnd](i/isMonthEnd.html), [isMonthStart](i/isMonthStart.html), [isQuarterEnd](i/isQuarterEnd.html), [isQuarterStart](i/isQuarterStart.html), [isYearEnd](i/isYearEnd.html), [isYearStart](i/isYearStart.html), [lastWeekOfMonth](l/lastWeekOfMonth.html), [listAllMarkets](l/listAllMarkets.html), [localtime](l/localtime.html), [microsecond](m/microsecond.html), [millisecond](m/millisecond.html), [minuteOfHour](m/minuteOfHour.html), [month](m/month.html), [monthBegin](m/monthBegin.html), [monthEnd](m/monthEnd.html), [monthOfYear](m/monthOfYear.html), [nanosecond](n/nanosecond.html), [now](n/now.html), [quarterBegin](q/quarterBegin.html), [quarterEnd](q/quarterEnd.html), [secondOfMinute](s/secondOfMinute.html), [semiannualBegin](s/semiannualBegin.html), [semiannualEnd](s/semiannualEnd.html), [semiMonthBegin](s/semiMonthBegin.html), [semiMonthEnd](s/semiMonthEnd.html), [temporalAdd](t/temporalAdd.html), [temporalDeltas](t/temporalDeltas.html), [temporalDiff](t/temporalDiff.html), [temporalSeq](t/temporalSeq.html), [today](t/today.html), [transFreq](t/transFreq.html), [updateMarketHoliday](u/updateMarketHoliday.html), [weekBegin](w/weekBegin.html), [weekday](w/weekday.html), [weekEnd](w/weekEnd.html), [weekOfMonth](w/weekOfMonth.html), [weekOfYear](w/weekOfYear.html), [year](y/year.html), [yearBegin](y/yearBegin.html), [yearEnd](y/yearEnd.html)
- **文本搜索/匹配：**[matchAll](m/matchall.html), [matchAny](m/matchany.html), [matchFuzzy](m/matchFuzzy.html), [matchPhrase](m/matchphrase.html), [matchPhraseInfix](m/matchphraseinfix.html), [matchPhrasePrefix](m/matchphraseprefix.html), [matchPhraseSuffix](m/matchphrasesuffix.html), [matchPrefix](m/matchprefix.html), [matchPrefixSuffix](m/matchprefixsuffix.html), [matchSpan](m/matchspan.html), [matchSuffix](m/matchsuffix.html), [matchUnorderedSpan](m/matchunorderedspan.html), [recursiveSplitText](r/recursiveSplitText.html), [tokenize](t/tokenize.html)

## 数据库/数据表

- **库表操作：**[addColumn](a/addColumn.html), [addFunctionView](a/addFunctionView.html), [addRangePartitions](a/addRangePartitions.html), [addValuePartitions](a/addValuePartitions.html), [backup](b/backup.html), [backupDB](b/backupDB.html), [backupTable](b/backupTable.html),
  [cacheDS!](c/cacheDS_.html), [cacheDSNow](c/cacheDSNow.html), [cachedTable](c/cachedTable.html), [checkBackup](c/checkBackup.html), [checkpointHaMvcc](c/checkpointHaMvcc.html), [clearAllTSDBSymbolBaseCache](c/clearalltsdbsymbolbasecache.html), [clearDSCache!](c/clearDSCache_.html), [clearDSCacheNow](c/clearDSCacheNow.html), [columnNames](c/columnNames.html), [createDimensionTable](c/createdimensiontable.html), [createDistributedInMemoryTable](c/createDistributedInMemoryTable.html), [createIPCInMemoryTable](c/createIPCInMemoryTable.html),
  [createPartitionedTable](c/createPartitionedTable.html), [createTable](c/createTable.html), [database](d/database.html), [disableActivePartition](d/disableActivePartition.html),
  [disableQueryMonitor](d/disableQueryMonitor.html), [disableTSDBAsyncSorting](d/disableTSDBAsyncSorting.html), [dropColumns!](d/dropColumns_.html), [dropDatabase](d/dropDatabase.html), [dropDistributedInMemoryTable](d/dropDistributedInMemoryTable.html), [dropFunctionView](d/dropFunctionView.html), [dropHaMvccTable](d/dropHaMvccTable.html), [dropIPCInMemoryTable](d/dropIPCInMemoryTable.html), [dropPartition](d/dropPartition.html), [dropTable](d/dropTable.html), [enableActivePartition](e/enableActivePartition.html), [enableQueryMonitor](e/enableQueryMonitor.html), [enableTSDBAsyncSorting](e/enableTSDBAsyncSorting.html), [existsDatabase](e/existsDatabase.html), [existsPartition](e/existsPartition.html), [existsTable](e/existsTable.html), [extractTextSchema](e/extractTextSchema.html), [flushOLAPCache](f/flushOLAPCache.html), [flushTSDBCache](f/flushTSDBCache.html), [getAllDBGranularity](g/getAllDBGranularity.html), [getAllDBs](g/getAllDBs.html), [getBackupList](g/getBackupList.html), [getBackupMeta](g/getBackupMeta.html), [getBackupStatus](g/getBackupStatus.html), [getChunkPath](g/getChunkPath.html), [getChunksMeta](g/getChunksMeta.html), [getClusterChunksStatus](g/getClusterChunksStatus.html), [getClusterDFSDatabases](g/getClusterDFSDatabases.html),
  [getClusterDFSTables](g/getClusterDFSTables.html),
  [getClusterVolumeUsage](g/getClusterVolumeUsage.html), [getConfigure](g/getConfigure.html)/[getConfig](g/getConfig.html), [getDFSDatabases](g/getDFSDatabases.html), [getDFSDatabasesByOwner](g/getdfsdatabasebyowner.html), [getDFSTablesByDatabase](g/getDFSTablesByDatabase.html),
  [getFunctionViews](g/getFunctionViews.html), [getHaMvccLeader](g/getHaMvccLeader.html), [getHaMvccRaftGroups](g/getHaMvccRaftGroups.html), [getHaMvccTableInfo](g/getHaMvccTableInfo.html), [getLevelFileIndexCacheStatus](g/getLevelFileIndexCacheStats.html), [getLocalIOTDBStaticTable](g/getLocalIOTDBStaticTable.html),
  [getMemLimitOfQueryResult](g/getMemLimitOfQueryResult.html), [getMemLimitOfTaskGroupResult](g/getMemLimitOfTaskGroupResult.html), [getOLAPCacheEngineSize](g/getOLAPCacheEngineSize.html),
  [getOLAPCacheEngineStat](g/getOLAPCacheEngineStat.html), [getOLAPCachedSymbolBaseMemSize](g/getOLAPCachedSymbolBaseMemSize.html),
  [getPKEYCompactionTaskStatus](g/getpkeycompactiontaskstatus.html), [getPKEYMetaData](g/getpkeymetadata.html),
  [getRecoveryTaskStatus](g/getRecoveryTaskStatus.html),
  [getRecoveryWorkerNum](g/getRecoveryWorkerNum.html),
  [getRedoLogGCStat](g/getRedoLogGCStat.html), [getTables](g/getTables.html), [getTablet](g/getTablet.html), [getTabletsMeta](g/getTabletsMeta.html), [getTransactionStatus](g/getTransactionStatus.html), [getTSDBCachedSymbolBaseMemSize](g/getTSDBCachedSymbolBaseMemSize.html), [getTSDBCacheEngineSize](g/getTSDBCacheEngineSize.html),
  [getTSDBCompactionTaskStatus](g/getTSDBCompactionTaskStatus.html), [getTSDBMetaData](g/getTSDBMetaData.html), [getUnresolvedTxn](g/getUnresolvedTxn.html), [haMvccTable](h/haMvccTable.html), [imr](i/imr.html), [indexedTable](i/indexedTable.html), [isCheckpointingHaMvcc](i/isCheckpointingHaMvcc.html), [keyedTable](k/keyedTable.html), [latestIndexedTable](l/latestIndexedTable.html), [latestKeyedStreamTable](l/latestkeyedstreamtable.html),
  [latestKeyedTable](l/latestKeyedTable.html), [listTables](l/listTables.html), [loadBackup](l/loadBackup.html), [loadDistributedInMemoryTable](l/loadDistributedInMemoryTable.html), [loadHaMvccTable](l/loadHaMvccTable.html), [loadIPCInMemoryTable](l/loadIPCInMemoryTable.html), [loadMvccTable](l/loadMvccTable.html), [loadTableBySQL](l/loadTableBySQL.html), [migrate](m/migrate.html), [mr](m/mr.html),
  [multiTableRepartitionDS](m/multiTableRepartitionDS.html), [mvccTable](m/mvccTable.html), [purgeCacheEngine](p/purgeCacheEngine.html), [rename!](r/rename_.html),
  [renameTable](r/renameTable.html), [reorderColumns!](r/reorderColumns_.html), [repartitionDS](r/repartitionDS.html), [replaceColumn!](r/replaceColumn_.html), [replay](r/replay.html), [replayDS](r/replayDS.html), [resetRecoveryWorkerNum](r/resetRecoveryWorkerNum.html), [restore](r/restore.html), [restoreDB](r/restoreDB.html), [restoreTable](r/restoreTable.html), [matchedRowCount](m/matchedrowcount.html), [rowNames](r/rowNames.html), [rowNo](r/rowNo.html), [runExternalQuery,](r/runexternalquery.html)
  [saveDatabase](s/saveDatabase.html), [saveDualPartition](s/saveDualPartition.html), [savePartition](s/savePartition.html), [saveTable](s/saveTable.html), [schema](s/schema.html), [setAtomicLevel](s/setAtomicLevel.html), [setChunkLastUpdateTime](s/setChunkLastUpdateTime.html), [setColumnComment](s/setColumnComment.html), [setHaMvccColumnDefaultValue](s/setHaMvccColumnDefaultValue.html), [setHaMvccColumnNullability](s/setHaMvccColumnNullability.html), [setMaxBlockSizeForReservedMemory](s/setMaxBlockSizeForReservedMemory.html), [setMaxConnections](s/setMaxConnections.html), [setMaxMemSize](s/setMaxMemSize.html), [setMemLimitOfQueryResult](s/setMemLimitOfQueryResult.html),
  [setMemLimitOfTaskGroupResult](s/setMemLimitOfTaskGroupResult.html), [setMemLimitOfTempResult](s/setMemLimitOfTempResult.html), [setOLAPCacheEngineSize](s/setOLAPCacheEngineSize.html),
  [setReservedMemSize](s/setReservedMemSize.html),
  [setTableComment](s/settablecomment.html), [setTSDBCacheEngineSize](s/setTSDBCacheEngineSize.html), [sqlDS](s/sqlDS.html), [table](t/table.html), [tableInsert](t/tableInsert.html), [tableUpsert](t/tableUpsert.html), [textChunkDS](t/textChunkDS.html), [transDS!](t/transDS_.html), [triggerTSDBCompaction](t/triggerTSDBCompaction.html),
  [truncate](t/truncate.html), [tupleSum](t/tupleSum.html), [update!](u/update_.html), [upsert!](u/upsert_.html)
- **catalog相关操作：**[createCatalog](c/createCatalog.html), [createSchema](c/createSchema.html), [dropCatalog](d/dropCatalog.html), [dropSchema](d/dropSchema.html), [existsCatalog](e/existsCatalog.html), [getAllCatalogs](g/getAllCatalogs.html), [getCurrentCatalog](g/getCurrentCatalog.html), [getSchemaByCatalog](g/getSchemaByCatalog.html), [renameCatalog](r/renameCatalog.html), [renameSchema](r/renameSchema.html), [setDefaultCatalog](s/setDefaultCatalog.html)
- **集群操作：**[addNode](a/addNode.html), [addVolumes](a/addVolumes.html), [cancelRecoveryTask](c/cancelRecoveryTask.html), [copyReplicas](c/copyReplicas.html), [deleteReplicas](d/deleteReplicas.html), [getActiveMaster](g/getActiveMaster.html), [getActiveMaster](g/getActiveMaster.html), [getConnections](g/getConnections.html), [getDatabaseClusterReplicationStatus](g/getDatabaseClusterReplicationStatus.html), [getMasterReplicationStatus](g/getMasterReplicationStatus.html), [getNodeAlias](g/getNodeAlias.html), [getNodeHost](g/getNodeHost.html), [getNodePort](g/getNodePort.html),
  [getNodeType](g/getNodeType.html), [getRecentSlaveReplicationInfo](g/getRecentSlaveReplicationInfo.html), [getSlaveReplicationStatus](g/getSlaveReplicationStatus.html), [getSlaveReplicationQueueStatus](g/getslavereplicationqueuestatus.html),
  [isControllerInitialized](i/isControllerInitialized.html),
  [isDataNodeInitialized](i/isDataNodeInitialized.html),
  [moveChunksAcrossVolume](m/moveChunksAcrossVolume.html), [moveReplicas](m/moveReplicas.html), [pnodeRun](p/pnodeRun.html),
  [rebalanceChunksAmongDataNodes](r/rebalanceChunksAmongDataNodes.html), [rebalanceChunksWithinDataNode](r/rebalanceChunksWithinDataNode.html), [remoteRun](r/remoteRun.html), [remoteRunCompatible](r/remoteruncompatible.html), [remoteRunWithCompression](r/remoteRunWithCompression.html),
  [removeNode](r/removenode.html), [resetDBDirMeta](r/resetDBDirMeta.html), [restoreDislocatedTablet](r/restoreDislocatedTablet.html),
  [resumeRecovery](r/resumeRecovery.html), [rpc](r/rpc.html), [setDatabaseForClusterReplication](s/setDatabaseForClusterReplication.html), [setTimeoutTick](s/setTimeoutTick.html), [skipClusterReplicationTask](s/skipClusterReplicationTask.html), [startClusterReplication](s/startClusterReplication.html),
  [startDataNode](s/startDataNode.html), [stopClusterReplication](s/stopClusterReplication.html),
  [stopDataNode](s/stopDataNode.html), [suspendRecovery](s/suspendRecovery.html), [triggerNodeReport](t/triggerNodeReport.html), [xdb](x/xdb.html)
- **多集群操作：**[getAllClusters](g/getAllClusters.html), [getCatalogsByCluster](g/getCatalogsByCluster.html), [getClusterStatus](g/getClusterStatus.html), [getDatabasesByCluster](g/getDatabasesByCluster.html), [getGroupAccessByCluster](g/getGroupAccessByCluster.html),
  [getGroupListOfAllClusters](g/getGroupListOfAllClusters.html), [getSchemasByCluster](g/getSchemasByCluster.html), [getTableAccessByCluster](g/getTableAccessByCluster.html),
  [getTablesByCluster](g/getTablesByCluster.html), [getTablesOfAllClusters](g/getTablesOfAllClusters.html),
  [getTableSchemaByCluster](g/getTableSchemaByCluster.html), [getUserAccessByCluster](g/getUserAccessByCluster.html),
  [getUserListOfAllClusters](g/getUserListOfAllClusters.html), [listPluginsByCluster](l/listPluginsByCluster.html)
- **计算组相关操作：**[addCacheRulesForComputeGroup](a/addcacherulesforcomputegroup.html), [clearComputeNodeCache](c/clearcomputenodecache.html), [clearComputeNodeDiskCache](c/clearcomputenodediskcache.html), [enableTransferCompressionToComputeNode](e/enabletransfercompressiontocomputenode.html), [flushComputeNodeMemCache](f/flushcomputenodememcache.html),
  [getCacheRulesForComputeGroup](g/getcacherulesforcomputegroup.html), [getComputeGroupChunksStatus](g/getcomputegroupchunksstatus.html), [getComputeNodeCacheDetails](g/getComputeNodeCacheDetails.html), [getComputeNodeCacheStat](g/getcomputenodecachestat.html),
  [getComputeNodeCacheWarmupJobStatus](g/getcomputenodecachewarmupjobstatus.html), [getComputeNodeCachingDelay](g/getcomputenodecachingdelay.html), [getPrefetchComputeNodeData](g/getprefetchcomputenodedata.html), [isTransferCompressionToComputeNodeEnabled,](i/istransfercompressiontocomputenodeenabled.html)
  [removeCacheRulesForComputeGroup](r/removecacherulesforcomputegroup.html), [setComputeNodeCachingDelay](s/setcomputenodecachingdelay.html), [setPrefetchComputeNodeData](s/setprefetchcomputenodedata.html), [warmupComputeNodeCache](w/warmupcomputenodecache.html)

## SQL

- **关键字：**[alter](../progr/sql/alter.html), [any/all](../progr/sql/any.html), [between](../progr/sql/between.html), [case](../progr/sql/case.html), [cgroup by](../progr/sql/cgroupby.html), [coalesce](../progr/sql/coalesce.html), [context by](../progr/sql/contextBy.html), [create](../progr/sql/create.html), [delete](../progr/sql/delete.html), [distinct](../progr/sql/distinct.html), [drop](../progr/sql/drop.html), [exec](../progr/sql/exec.html), [exists](../progr/sql/exists.html), [group by](../progr/sql/groupby.html), [having](../progr/sql/having.html), [[HINT\_EXPLAIN](../progr/sql/hint_explain.html)], [in](../progr/sql/in.html), [insert into](../progr/sql/insertInto.html), [interval](../progr/sql/interval.html), [is null](../progr/sql/isnull.html),
  [like/LIKE](../progr/sql/like.html), [limit](../progr/sql/limit.html), [map](../progr/sql/map.html), [notBetween/NOTBETWEEN](../progr/sql/notbetween.html), [notIn/NOTIN](../progr/sql/notin.html), [notLike/NOTLIKE](../progr/sql/notlike.html), [nullIf](n/nullIf.html), [order by](../progr/sql/orderby.html), [over](../progr/sql/analyticFunction.html), [partition](../progr/sql/partition.html), [pivot by](../progr/sql/pivotBy.html), [sample](../progr/sql/sample.html), [select](../progr/sql/Select.html), [SQL Trace](../progr/sql/sql_trace.html), [top](../progr/sql/top.html), [union/union all](../progr/sql/union.html), [unpivot](u/unpivot.html), [update](../progr/sql/update.html), [where](../progr/sql/where.html), [with](../progr/sql/with.html)
- **表连接：**[aj](../progr/sql/asofjoin.html), [cj](../progr/sql/crossjoin.html), [ej](../progr/sql/equijoin.html), [fj](../progr/sql/fulljoin.html) (full join), [inner join](../progr/sql/innerjoin.html), [lj](../progr/sql/leftjoin.html) (left join), [lsj](../progr/sql/leftjoin.html) (left semi join), [pj](../progr/sql/prefixjoin.html), [pwj](../progr/sql/windowjoin.html), [right join](../progr/sql/rightjoin.html),
  [sej](../progr/sql/equijoin.html), [wj](../progr/sql/windowjoin.html)
- **状态查看：**[getCompletedQueries](g/getCompletedQueries.html), [getQueryStatus](g/getQueryStatus.html), [getRunningQueries](g/getRunningQueries.html), [getTraces](../progr/sql/getTraces.html), [setTraceMode](../progr/sql/setTraceMode.html), [viewTraceInfo](../progr/sql/viewTraceInfo.html)

## 数学和统计

- **数学：**[abs](a/abs.html), [acos](a/acos.html), [acosh](a/acosh.html), [add](a/add.html), [asin](a/asin.html),
  [asinh](a/asinh.html), [atan](a/atan.html), [atanh](a/atanh.html), [cbrt](c/cbrt.html), [clip](c/clip.html),
  [clip!](c/clip_.html), [cos](c/cos.html), [cosh](c/cosh.html), [cholesky](c/cholesky.html), [derivative](d/derivative.html), [diag](d/diag.html), [div](d/div.html), [det](d/det.html), [eig](e/eig.html), [exp](e/exp.html), [exp2](e/exp2.html), [expm1](e/expm1.html),
  [gram](g/gram.html), [gramSchmidt](g/gramSchmidt.html), [integral](i/integral.html), [inverse](i/inverse.html), [intersection](i/intersection.html), [iterate](i/iterate.html), [log](l/log.html), [log1p](l/log1p.html),
  [log2](l/log2.html), [log10](l/log10.html), [lu](l/lu.html), [mod](m/mod.html), [mul](m/mul.html), [neg](n/neg.html), [pow](p/pow.html), [ratio](r/ratio.html), [reciprocal](r/reciprocal.html), [repmat](r/repmat.html), [sin](s/sin.html), [sinh](s/sinh.html),
  [sqrt](s/sqrt.html), [square](s/square.html), [sub](s/sub.html), [symmetricDifference](s/symmetricDifference.html), [svd](s/svd.html), [tan](t/tan.html), [tanh](t/tanh.html), [tril](t/tril.html),
  [triu](t/triu.html), [schur](s/schur.html), [signbit](s/signbit.html), [signum](s/signum.html), [qr](q/qr.html)
- **统计：**[atImax](a/atImax.html), [atImin](a/atImin.html), [avg](a/avg.html),
  [boxcox](b/boxcox.html), [contextCount](c/contextCount.html), [contextSum](c/contextSum.html),
  [contextSum2](c/contextSum2.html), [count](c/count.html), [covar](c/covar.html), [covarp](c/covarp.html), [covarMatrix](c/covarMatrix.html), [crossStat](c/crossStat.html), [cubicHermiteSplineFit](c/cubichermitesplinefit.html), [cumnunique](c/cumnunique.html), [demean](d/demean.html), [dot](d/dot.html), [ewmCov](e/ewmCov.html), [ewmMean](e/ewmMean.html), [ewmStd](e/ewmStd.html), [ewmVar](e/ewmVar.html), [gaussianKde](g/gaussiankde.html), [gaussianKdePredict](g/gaussiankdepredict.html), [imax](i/imax.html), [imin](i/imin.html), [kurtosis](k/kurtosis.html), [mad](m/mad.html), [max](m/max.html), [maxIgnoreNull](m/maxignorenull.html), [med](m/med.html), [mean](m/mean.html), [min](m/min.html),
  [minIgnoreNull](m/minignorenull.html), [mode](m/mode.html), [mmed](m/mmed.html),
  [nunique](n/nunique.html), [percentChange](p/percentChange.html), [percentile](p/percentile.html), [percentileRank](p/percentileRank.html), [prod](p/prod.html), [qcut](q/qcut.html),
  [quantile](q/quantile.html), [quantileSeries](q/quantileSeries.html), [rms](r/rms.html),[sem](s/sem.html), [skew](s/skew.html), [std](s/std.html),
  [stdp](s/stdp.html), [summary](s/summary.html), [sum](s/sum.html), [sum2](s/sum2.html), [sum3](s/sum3.html),
  [sum4](s/sum4.html), [stat](s/stat.html), [var](v/var.html), [varp](v/varp.html), [wavg](w/wavg.html),
  [wc](w/wc.html), [wcovar](w/wcovar.html), [wsum](w/wsum.html), [histogram](h/histogram.html), [histogram2d](h/histogram2d.html), [kroghInterpolateFit](k/kroghinterpolatefit.html), [linearInterpolateFit](l/linearinterpolatefit.html)
- **相关性：**[acf](a/acf.html), [autocorr](a/autocorr.html), [corr](c/corr.html), [corrMatrix](c/corrMatrix.html), [distance](d/distance.html), [ewmCorr](e/ewmCorr.html), [euclidean](e/euclidean.html), [kendall](k/kendall.html), [mutualInfo](m/mutualInfo.html), [rowEuclidean](r/rowEuclidean.html), [rowTanimoto](r/rowTanimoto.html), [spearmanr](s/spearmanr.html), [tanimoto](t/tanimoto.html), [cosine](c/cosine.html)
- **序列分析：**[isMonotonicIncreasing](i/isMonotonicIncreasing.html)/[isMonotonic](i/isMonotonic.html), [isMonotonicDecreasing](i/isMonotonicDecreasing.html), [isPeak](i/isPeak.html),
  [isValley](i/isValley.html), [zigzag](z/zigzag.html)[isMonotonicDecreasing](i/isMonotonicDecreasing.html)
- **分布与假设检验：**[adfuller](a/adfuller.html), [anova](a/anova.html), [cdfBeta](c/cdfBeta.html), [cdfBinomial](c/cdfBinomial.html), [cdfChiSquare](c/cdfChiSquare.html), [cdfExp](c/cdfExp.html), [cdfF](c/cdfF.html), [cdfGamma](c/cdfGamma.html), [cdfKolmogorov](c/cdfKolmogorov.html), [cdfLogistic](c/cdfLogistic.html),
  [cdfNormal](c/cdfNormal.html), [cdfPoisson](c/cdfPoisson.html), [cdfStudent](c/cdfStudent.html), [cdfUniform](c/cdfUniform.html), [cdfWeibull](c/cdfWeibull.html), [cdfZipf](c/cdfZipf.html), [chiSquareTest](c/chiSquareTest.html),
  [coint](c/coint.html),
  [esd](e/esd.html), [fTest](f/fTest.html), [invBeta](i/invBeta.html), [invBinomial](i/invBinomial.html), [invChiSquare](i/invChiSquare.html), [invExp](i/invExp.html), [invF](i/invF.html), [invGamma](i/invGamma.html), [invLogistic](i/invLogistic.html), [invNormal](i/invNormal.html), [invStudent](i/invStudent.html), [invPoisson](i/invPoisson.html),
  [invUniform](i/invUniform.html), [invWeibull](i/invWeibull.html), [ksTest](k/ksTest.html), [mannWhitneyUTest](m/mannWhitneyUTest.html), [manova](m/manova.html),
  [norm](n/norm.html)/[normal](n/normal.html), [rand](r/rand.html), [randBeta](r/randBeta.html), [randBinomial](r/randBinomial.html), [randChiSquare](r/randChiSquare.html), [randDiscrete](r/randDiscrete.html), [randExp](r/randExp.html), [randF](r/randF.html), [randGamma](r/randGamma.html), [randLogistic](r/randLogistic.html),
  [randMultivariateNormal](r/randMultivariateNormal.html), [randNormal](r/randNormal.html), [randPoisson](r/randPoisson.html),
  [randStudent](r/randStudent.html), [randUniform](r/randUniform.html), [randWeibull](r/randWeibull.html), [seasonalEsd](s/seasonalEsd.html), [shapiroTest](s/shapiroTest.html), [tTest](t/tTest.html), [zTest](z/zTest.html)
- **数据处理：**[all](a/all.html), [any](a/any.html), [asis](a/asIs.html), [asof](a/asof.html), [bucketCount](b/bucketCount.html), [coevent](c/coevent.html), [cols](c/cols.html), [deepCopy](d/deepCopy.html), [copy](c/copy.html), [countNanInf](c/countNanInf.html), [cumPositiveStreak](c/cumPositiveStreak.html), [deltas](d/deltas.html), [dictUpdate!](d/dictUpdate_.html),[difference](d/difference.html),
  [distinct](d/distinct.html), [dynamicGroupCumcount](d/dynamicGroupCumcount.html), [dynamicGroupCumsum](d/dynamicGroupCumsum.html), [hashBucket](h/hashBucket.html), [iif](i/iif.html), [imaxLast](i/imaxlast.html), [iminLast](i/iminlast.html), [isDuplicated](i/isDuplicated.html),[keys](k/keys.html), [linearTimeTrend](l/linearTimeTrend.html), [lowerBound](l/lowerbound.html), [lowRange](l/lowRange.html), [mask](m/mask.html), [maxPositiveStreak](m/maxPositiveStreak.html), [mimaxLast](m/mimaxlast.html), [miminLast](m/miminlast.html), [mmaxPositiveStreak](m/mmaxPositiveStreak.html), [pca](p/pca.html), [ratios](r/ratios.html),
  [resample](r/resample.html), [rowImaxLast](r/rowimaxlast.html), [rowIminLast](r/rowiminlast.html), [rows](r/rows.html), [sessionWindow](s/sessionWindow.html),
  [shape](s/shape.html), [size](s/size.html), [stl](s/stl.html), [sumbars](s/sumbars.html), [talibNull](t/talibNull.html), [tmove](t/tmove.html), [topRange](t/topRange.html), [valueChanged](v/valueChanged.html), [values](v/values.html), [winsorize!](w/winsorize_.html), [winsorize](w/winsorize.html), [zscore](z/zscore.html), [differentialEvolution](d/differentialevolution.html)
- **插值:**
  [cubicSpline](c/cubicspline.html), [cubicSplinePredict](c/cubicsplinepredic.html), [dividedDifference](d/dividedDifference.html), [kroghInterpolate](k/kroghinterpolate.html), [loess](l/loess.html), [neville](n/neville.html), [pchipInterpolateFit](p/pchipInterpolateFit.html), [spline](s/spline.html),
  [splrep](s/splrep.html), [splev](s/splev.html)
- **优化：**[brute](b/brute.html),
  [brentq](b/brentq.html), [fmin](f/fmin.html), [fminBFGS](f/fminbfgs.html), [fminLBFGSB](f/fminlbfgsb.html),
  [fminNCG](f/fminncg.html), [fminSLSQP](f/fminslsqp.html), [linprog](l/linprog.html), [osqp](o/osqp.html), [qclp](q/qclp.html), [quadprog](q/quadprog.html), [scs](s/scs.html), [solve](s/solve.html), [socp](s/socp.html)[brentq](b/brentq.html)

## 运算符

- **逻辑：**[and](a/and.html), [bitAnd](b/bitAnd.html), [bitNot](b/bitNot.html), [bitOr](b/bitOr.html), [bitXor](b/bitXor.html), [not](n/not.html), [or](o/or.html), [xor](x/xor.html)
- **关系：**[between](b/between.html), [eq](e/eq.html), [eqFloat](e/eqFloat.html), [eqObj](e/eqObj.html), [eqPercent](e/eqpercent.html), [ge](g/ge.html), [gt](g/gt.html), [in](i/in.html), [le](l/le.html), [lt](l/lt.html), [ne](n/ne.html)

## 流数据

- **流表操作：**[appendForJoin](a/appendForJoin.html), [appendMsg](a/appendMsg.html), [changelogStreamTable](c/changelogStreamTable.html),
  [clearTablePersistence](c/clearTablePersistence.html),
  [createOrcaHaKeyedStreamTable](c/createOrcaHaKeyedStreamTable.html),
  [createOrcaHaStreamTable](c/createOrcaHaStreamTable.html),
  [createOrcaKeyedStreamTable](c/createOrcaKeyedStreamTable.html),
  [createOrcaLatestKeyedStreamTable](c/createOrcaLatestKeyedStreamTable.html),
  [createOrcaStreamTable](c/createOrcaStreamTable.html),
  [createStreamGraph](c/createStreamGraph.html),
  [emitEvent](e/emitEvent.html),
  [getOrcaStreamTableMeta](g/getOrcaStreamTableMeta.html), [getStreamGraph](getStreamGraph.html),
  [getStreamGraphInfo](getStreamGraphInfo.html),
  [getStreamGraphMeta](getStreamGraphMeta.html), [getStreamTableChangelog](g/getStreamTableChangelog.html), [resubmitStreamGraph](r/resubmitStreamGraph.html),
  [routeEvent](r/routeEvent.html),
  [sendEvent](s/sendEvent.html),
  [startStreamGraph](s/startStreamGraph.html),
  [stopStreamGraph](s/stopStreamGraph.html),
  [streamEventSerializer](s/streamEventSerializer.html), [streamFilter](s/streamFilter.html), [updateStreamGraphUserTickets](u/update_stream_graph_user_tickets.html),
  [useOrcaStreamTable](u/useOrcaStreamTable.html), [disableTablePersistence](d/disableTablePersistence.html),
  [dropStreamTable](d/dropStreamTable.html), [dropStreamGraph](d/dropStreamGraph.html),
  [dropOrcaStreamTable](d/dropOrcaStreamTable.html),
  [enableTableCachePurge](e/enabletablecachepurge.html),
  [enableTablePersistence](e/enableTablePersistence.html), [enableTableShareAndCachePurge](e/enabletableshareandcachepurge.html), [enableTableShareAndPersistence](e/enableTableShareAndPersistence.html), [existsStreamTable](e/existsStreamTable.html), [existsSubscriptionTopic](e/existsSubscriptionTopic.html),
  [getStreamTables](g/getstreamtables.html), [haStreamTable](h/haStreamTable.html), [keyedStreamTable](k/keyedStreamTable.html), [purgeStreamGraphRecords](purgeStreamGraphRecords.html), [removeTopicOffset](r/removeTopicOffset.html), [setStreamTableFilterColumn](s/setStreamTableFilterColumn.html), [setStreamTableTimestamp](s/setstreamtabletimestamp.html), [share](../progr/statements/share.html), [subscribeTable](s/subscribeTable.html), [unsubscribeTable](u/unsubscribeTable.html), [streamTable](s/streamTable.html)
- **计算引擎：**[createAnomalyDetectionEngine](c/createAnomalyDetectionEngine.html), [createAsofJoinEngine](c/createAsofJoinEngine.html), [createCrossSectionalEngine](c/createCrossSectionalEngine.html), [createCEPEngine](c/createCEPEngine.html),
  [createCrossSectionalAggregator](c/createCrossSectionalAggregator.html), [createDataViewEngine](c/createDataViewEngine.html),
  [createDeviceEngine](c/createdeviceengine.html),
  [createGPLearnEngine](c/creategplearnengine.html), [createNearestJoinEngine](c/createNearestJoinEngine.html),
  [createOrderReconstituteEngine](c/createsseorderreconstructionengine.html), [createReactiveStatelessEngine](c/createReactiveStatelessEngine.html), [createStreamBroadcastEngine](c/createstreambroadcastengine.html), [createThresholdEngine](c/createthresholdengine.html), [createTimeSeriesAggregator](c/createTimeSeriesAggregator.html), [getCEPEngineMonitor](g/getCEPEngineMonitor.html),
  [getCEPEngineStat](g/getCEPEngineStat%20.html),
  [getCEPEngineSubMonitor](g/getCEPEngineSubMonitor.html),
  [getDataViewEngine](g/getDataViewEngine.html),
  [stopSubEngine](s/stopSubEngine.html),
  [updateDataViewItems](u/updateDataViewItems.html),
  [useOrcaStreamEngine](u/useOrcaStreamEngine.html),
  [warmupOrcaStreamEngine](w/warmupOrcaStreamEngine.html),, [createDailyTimeSeriesEngine](c/createDailyTimeSeriesEngine.html), [createDualOwnershipReactiveStateEngine](c/createDualOwnershipReactiveStateEngine.html), [createEquiJoinEngine](c/createEquiJoinEngine.html)/ [createEqualJoinEngine](c/createEqualJoinEngine.html), [createLeftSemiJoinEngine](c/createLeftSemiJoinEngine.html),
  [createLookupJoinEngine](c/createLookupJoinEngine.html), [createNarrowReactiveStateEngine](c/createnarrowreactivestateengine.html), [createOrderBookSnapshotEngine](c/createorderbooksnapshotengine.html), [createReactiveStateEngine](c/createReactiveStateEngine.html), [createRuleEngine](c/createRuleEngine.html), [createSessionWindowEngine](c/createSessionWindowEngine.html), [createSnapshotJoinEngine](c/createsnapshotjoinengine.html), [createSparseReactiveStateEngine](c/createSparseReactiveStateEngine.html), [createStreamDispatchEngine](c/createStreamDispatchEngine.html), [createTimeBucketEngine](c/createtimebucketengine.html), [createTimeSeriesEngine](c/createTimeSeriesEngine.html),
  [createWindowJoinEngine](c/createWindowJoinEngine.html), [streamEngineParser](s/streamEngineParser.html), [createCryptoOrderBookEngine](c/createcryptoorderbookengine.html)
- **工具函数：**[addMetrics](a/addMetrics.html), [addReactiveMetrics](a/addreactivemetrics.html), [addSparseReactiveMetrics](a/addSparseReactiveMetrics.html),
  [addStatelessMetrics](a/addstatelessmetrics.html), [conditionalIterate](c/conditionalIterate.html), [dropDataViewEngine](d/dropDataViewEngine.html), [deleteRule](d/deleteRule.html), [deleteSparseReactiveMetric](d/deleteSparseReactiveMetric.html), [dropStreamEngine](d/dropStreamEngine.html)/ [dropAggregator](d/dropAggregator.html), [getComputeNodeCacheWarmupJobStatus](g/getcomputenodecachewarmupjobstatus.html), [forceTriggerOrderBookSnapshot](f/forceTriggerOrderBookSnapshot.html), [getLeftStream](g/getLeftStream.html)/[getRightStream](g/getRightStream.html), [getPersistenceMeta](g/getPersistenceMeta.html), [getReactiveMetrics](g/getreactivemetrics.html), [getSnapshotMsgId](g/getSnapshotMsgId.html), [getSparseReactiveMetrics](g/getSparseReactiveMetrics.html),
  [getStatelessMetrics](g/getstatelessmetrics.html), [getStreamEngine](g/getStreamEngine.html)/[getAggregator](g/getAggregator.html), [getStreamEngineList](g/getstreamenginelist.html), [getStreamEngineStat](g/getStreamEngineStat.html)/[getAggregatorStat](g/getAggregatorStat.html), [getRules](g/getrules.html), [getStreamingLeader](g/getStreamingLeader.html), [getStreamingRaftGroups](g/getStreamingRaftGroups.html), [getStreamingStat](g/getStreamingStat.html), [getStreamTableCacheOffset](g/getstreamtablecacheoffset.html), [getStreamTableFilterColumn](g/getStreamTableFilterColumn.html), [getSubscriptionTopic](g/getSubscriptionTopic.html), [getTopicProcessedOffset](g/getTopicProcessedOffset.html),
  [stateIterate](s/stateIterate.html), [warmupComputeNodeCache](w/warmupcomputenodecache.html),
  [warmupStreamEngine](w/warmupStreamEngine.html)
- **流式 SQL：**[declareStreamingSQLTable](d/declareStreamingSQLTable.html),
  [getStreamingSQLStatus](g/getStreamingSQLStatus.html),
  [listStreamingSQLTables](l/listStreamingSQLTables.html), [registerStreamingSQL](r/registerStreamingSQL.html), [revokeStreamingSQL](r/revokeStreamingSQL.html), [revokeStreamingSQLTable](r/revokeStreamingSQLTable.html), [subscribeStreamingSQL](s/subscribeStreamingSQL.html), [unsubscribeStreamingSQL](u/unsubscribeStreamingSQL.html),[getStreamingSQLSubscriptionInfo](g/getstreamingsqlsubscriptioninfo.html)

## 元编程

[addGpFunction](a/addgpfunction.html),
[encryptModule](e/encryptmodule.html), [installModule](i/installmodule.html), [listRemoteModules](l/listremotemodules.html), [setGpFitnessFunc](s/setgpfitnessfunc.html), [binaryExpr](b/binaryExpr.html), [eval](e/eval.html), [expr](e/expr.html), [funcByName](f/funcByName.html), [makeCall](m/makeCall.html), [makeUnifiedCall](m/makeUnifiedCall.html), [parseExpr](p/parseExpr.html), [sql](s/sql.html), [sqlCol](s/sqlCol.html), [sqlColAlias](s/sqlColAlias.html), [sqlDelete](s/sqlDelete.html), [sqlUpdate](s/sqlUpdate.html), [unifiedExpr](u/unifiedExpr.html)

## 高阶函数

[accumulate (:A)](ho_funcs/accumulate.html),
[aggrTopN](ho_funcs/aggrTopN.html), [all](ho_funcs/all.html), [any](ho_funcs/any.html), [byColumn (:V)](ho_funcs/byColumn.html), [byRow (:H)](ho_funcs/byRow.html), [call](ho_funcs/call.html), [compose](c/compose.html), [contextby (:X)](ho_funcs/contextby.html), [cross (:C)](ho_funcs/cross.html)/[pcross](ho_funcs/pcross.html), [each (:E)](ho_funcs/each.html), [eachLeft (:L)](ho_funcs/eachLeft.html),
[eachPost (:O)](ho_funcs/eachPost.html), [eachPre (:P)](ho_funcs/eachPre.html), [eachRight (:R)](ho_funcs/eachRight.html), [groupby (:G)](ho_funcs/groupby.html), [loop (:U)](ho_funcs/loop.html) / [ploop](ho_funcs/ploop.html), [moving](ho_funcs/moving.html), [nothrowCall](ho_funcs/nothrowcall.html),
[nullCompare](ho_funcs/nullCompare.html), [pcall](ho_funcs/pcall.html), [pivot](ho_funcs/pivot.html), [reduce (:T)](ho_funcs/reduce.html), [rolling](ho_funcs/rolling.html), [rowGroupby](ho_funcs/rowgroupby.html), [segmentby](ho_funcs/segmentby.html), [talib](ho_funcs/talib.html), [tmoving](ho_funcs/tmoving.html), [twindow](ho_funcs/twindow.html), [unifiedCall](ho_funcs/unifiedCall.html), [window](ho_funcs/window.html), [withNullFill](ho_funcs/withNullFill.html), [movingValid](ho_funcs/movingvalid.html)

## 金融分析

- **金融分析：**[arima](a/arima.html), [nss](n/nss.html), [ns](n/ns.html),
  [condValueAtRisk](c/cvar.html),
  [nssPredict](n/nsspredict.html), [trueRange](t/trueRange.html), [valueAtRisk](v/var_0.html), [varma](v/varma.html), [bondCashflow](b/bondCashflow.html), [bondYield](b/bondyield.html),
  [treasuryConversionFactor](t/treasuryconversionfactor.html),
  [vanillaOption](v/vanillaoption.html), [maxDrawdown](m/maxdrawdown.html), [mdd](m/mdd.html), [cummdd](c/cummdd.html)
- **FICC：**[bondAccrInt](b/bondaccrint.html), [bondCalculator](b/bondCalculator.html), [bondInstrumentCalculator](b/bondinstrumentcalculator.html), [bondConvexity](b/bondconvexity.html), [bondDirtyPrice](b/bondDirtyPrice.html), [bondDuration](b/bondDuration.html), , [bondFuturesPricer](b/bondFuturesPricer.html), [bondPricer](b/bondPricer.html), [bondYieldCurveBuilder](b/bondYieldCurveBuilder.html),
  [cmFutAmericanOptionPricer](c/cmfutamericanoptionpricer.html), [cmFutEuropeanOptionPricer](c/cmfuteuropeanoptionpricer.html), [cmFutVolatilitySurfaceBuilder](c/cmFutVolatilitySurfaceBuilder.html), [curvePredict](c/curvePredict.html), [eqAmericanOptionPricer](e/eqamericanoptionpricer.html),
  [eqEuropeanOptionPricer](e/eqeuropeanoptionpricer.html), [eqProxyVolatilitySurfaceBuilder](e/eqproxyvolatilitysurfacebuilder.html), [eqVolatilitySurfaceBuilder](e/eqvolatilitysurfacebuilder.html), [fxEuropeanOptionPricer](f/fxEuropeanOptionPricer.html),
  [fxForwardPricer](f/fxForwardPricer.html), [fxSwapPricer](f/fxSwapPricer.html), [fxVolatilitySurfaceBuilder](f/fxVolatilitySurfaceBuilder.html), [instrumentPricer](i/instrumentPricer.html), [irCrossCurrencyCurveBuilder](i/irCrossCurrencyCurveBuilder.html), [irDepositPricer](i/irDepositPricer.html), [irFixedFloatingSwapPricer](i/irFixedFloatingSwapPricer.html), [irSingleCurrencyCurveBuilder](i/irSingleCurrencyCurveBuilder.html), [optionVolPredict](o/optionVolPredict.html), [portfolioPricer](p/portfolioPricer.html)
- **FICC 工具：**[extractInstrument](e/extractInstrument.html), [extractMktData](e/extractMktData.html), [parseInstrument](p/parseInstrument.html), [parseMktData](p/parseMktData.html), [getInstrumentCalendar](g/getinstrumentcalendar.html), [getInstrumentCoupon](g/getInstrumentCoupon.html), [getInstrumentCreditRating](g/getinstrumentcreditrating.html), [getInstrumentCurrency](g/getinstrumentcurrency.html), [getInstrumentCurrencyPair](g/getinstrumentcurrencypair.html), [getInstrumentDayCountConvention](g/getInstrumentDayCountConvention.html), [getInstrumentDelivery](g/getinstrumentdelivery.html), [getInstrumentDirection](g/getinstrumentdirection.html),
  [getInstrumentExpiry](g/getinstrumentexpiry.html),
  [getInstrumentFarDelivery](g/getinstrumentfardelivery.html), [getInstrumentFarExpiry](g/getinstrumentfarexpiry.html),
  [getInstrumentFarStrike](g/getInstrumentFarStrike.html), [getInstrumentField](g/getInstrumentField.html), [getInstrumentFixedDayCountConvention](g/getinstrumentfixeddaycountconvention.html), [getInstrumentFixedRate](g/getinstrumentfixedrate.html),
  [getInstrumentFloatingDayCountConvention](g/getinstrumentfloatingdaycountconvention.html), [getInstrumentFrequency](g/getinstrumentfrequency.html),
  [getInstrumentIborIndex](g/getinstrumentiborindex.html), [getInstrumentInstrumentId](g/getinstrumentinstrumentid.html), [getInstrumentIssuePrice](g/getinstrumentissueprice.html),
  [getInstrumentKeys](g/getInstrumentKeys.html), [getInstrumentMaturity](g/getinstrumentmaturity.html), [getInstrumentNearDelivery](g/getinstrumentneardelivery.html), [getInstrumentNearExpiry](g/getinstrumentnearexpiry.html),
  [getInstrumentNearStrike](g/getinstrumentnearstrike.html), [getInstrumentNominal](g/getinstrumentnominal.html), [getInstrumentNominalCouponRate](g/getinstrumentnominalcouponrate.html),
  [getInstrumentNotionalAmount](g/getinstrumentnotionalamount.html),[getInstrumentNotionalCurrency](g/getinstrumentnotionalcurrency.html), [getInstrumentPayReceive](g/getinstrumentpayreceive.html),
  [getInstrumentPayoffType](g/getinstrumentpayofftype.html), [getInstrumentRate](g/getinstrumentrate.html), [getInstrumentSettlement](g/getinstrumentsettlement.html), [getInstrumentSpread](g/getinstrumentspread.html), [getInstrumentStart](g/getinstrumentstart.html), [getInstrumentStrike](g/getinstrumentstrike.html), [getInstrumentSubType](g/getinstrumentsubtype.html), [getInstrumentUnderlying](g/getinstrumentunderlying.html), [getMktData](g/getMktData.html),
  [yearFrac](y/yearFrac.html)
- **实时计算引擎及工具函数：**
  [createMktDataEngine](c/createMktDataEngine.html), [createPricingEngine](c/createpricingengine.html), [appendMktData](a/appendMktData.html)[appendMktData](a/appendMktData.html)

## 机器学习

- **机器学习：**[adaBoostClassifier](a/adaBoostClassifier.html), [adaBoostRegressor](a/adaBoostRegressor.html), [beta](b/beta.html), [bvls](b/bvls.html), [elasticNet](e/elasticNet.html), [elasticNetCV](e/elasticNetCV.html), [gaussianNB](g/gaussianNB.html), [glm](g/glm.html), [gmm](g/gmm.html), [kernelRidge](k/kernelRidge.html), [kmeans](k/kmeans.html), [knn](k/knn.html), [lasso](l/lasso.html), [lassoBasic](l/lassoBasic.html), [lassoCV](l/lassoCV.html), [logisticRegression](l/logisticRegression.html), [mmse](m/mmse.html), [msl](m/mslr.html),
  [multinomialNB](m/multinomialNB.html), [ols](o/ols.html), [olsEx](o/olsEx.html),
  [piecewiseLinFit](p/piecewiselinfit.html), [poly1d](p/poly1d.html), [polyPredict](p/polyPredict.html), [polyFit](p/polyfit.html), [polynomial](p/polynomial.html), [predict](p/predict.html), [pwlfPredict](p/pwlfpredict.html),
  [randomForestClassifier](r/randomForestClassifier.html), [randomForestRegressor](r/randomForestRegressor.html), [residual](r/residual.html), [ridge](r/ridge.html), [ridgeBasic](r/ridgeBasic.html), [vectorAR](v/vectorar.html), [wls](w/wls.html), [garch](g/garch.html), [elasticNetBasic](e/elasticNetBasic.html), [eqDividendCurveBuilder](e/eqDividendCurveBuilder.html),
  [gpFit](g/gpfit.html),
  [gpPredict](g/gppredict.html),
  [mahalanobis](m/mahalanobis.html), [minkowski](m/minkowski.html), [pdfChiSquare](p/pdfChiSquare.html), [pdfF](p/pdfF.html), [pdfNormal](p/pdfNormal.html), [pinverse](p/pinverse.html), [power](p/power.html), [ridgeCV](r/ridgeCV.html), [seuclidean](s/seuclidean.html), [vectorNorm](v/vectornorm.html), [wslr](w/wslr.html), [wsum2](w/wsum2.html)
- **文本处理：**[loadVocab](l/loadVocab.html), [tokenizeBert](t/tokenizeBert.html),
  [unloadVocab](u/unloadVocab.html)

## 权限与安全

[addAccessControl](a/addAccessControl.html),
[addGroupMember](a/addGroupMember.html), [addIPBlackList](a/addipblacklist.html), [addIPWhiteList](a/addipwhitelist.html), [generateUserTicket](g/generateuserticket.html), [getAuthenticatedUserTicket](g/getauthenticateduserticket.html),
[getDBAccess](g/getDBAccess.html), [getIPBlackList](g/getipblacklist.html), [getIPWhiteList](g/getipwhitelist.html), [getUserLockedStatus](g/getUserLockedStatus.html), [getUserPasswordStatus](g/getUserPasswordStatus.html), [isClientAuth](i/isclientauth.html), [lockUser](l/lockUser.html), [oauthLogin](o/oauthlogin.html), [removeIPBlackList](r/removeipblacklist.html), [removeIPWhiteList](r/removeipblacklist.html), [backupSettings](b/backupsettings.html), [changePwd](c/changePwd.html), [createGroup](c/createGroup.html), [createUser](c/createUser.html), [deleteGroup](d/deleteGroup.html), [deleteGroupMember](d/deleteGroupMember.html), [deleteUser](d/deleteUser.html), [deny](d/deny.html), [getAuthenticatedUsers](g/getAuthenticatedUsers.html), [getGroupAccess](g/getGroupAccess.html), [getGroupList](g/getGroupList.html), [getGroupsByUserId](g/getGroupsByUserId.html), [getOauthClientSecret](g/getOauthClientSecret.html), [getUserAccess](g/getUserAccess.html), [getUserList](g/getUserList.html),
[getUsersByGroupId](g/getUsersByGroupId.html), [grant](g/grant.html), [isLoggedIn](i/isLoggedIn.html), [login](l/login.html), [logout](l/logout.html), [resetPwd](r/resetPwd.html), [restoreSettings](r/restoresettings.html), [revoke](r/revoke.html), [scramClientFinal](s/scramClientFinal.html), [scramClientFirst](s/scramClientFirst.html), [unlockUser](u/unlockUser.html)

## 文件系统

[cleanOutdateLogFiles](c/cleanOutdateLogFiles.html), [close](c/close.html), [exists](e/exists.html), [fflush](f/fflush.html), [file](f/file.html), [files](f/files.html), [loadModel](l/loadModel.html), [mkdir](m/mkdir.html), [print](p/print.html),
[run](r/run.html), [runSQL](r/runsql.html), [runScript](r/runScript.html), [read!](r/read_.html), [readBytes](r/readBytes.html), [readLine](r/readLine.html), [readLines](r/readLines.html), [readLines!](r/readLines_.html), [readObject](r/readObject.html), [readRecord!](r/readRecord_.html), [rm](r/rm.html), [rmdir](r/rmdir.html), [saveAsNpy](s/saveAsNpy.html), [saveModel](s/saveModel.html), [saveText](s/saveText.html), [saveTextFile](s/saveTextFile.html), [seek](s/seek.html), [write](w/write.html), [writeBytes](w/writeBytes.html), [writeLine](w/writeLine.html), [writeLines](w/writeLines.html), [writeLog](w/writeLog.html), [writeLogLevel](w/writeloglevel.html), [writeObject](w/writeObject.html),
[writeRecord](w/writeRecord.html)

## 系统管理

[addEventListener](a/addEventListener.html), [cancelPKEYCompactionTask](c/cancelpkeycompactiontask.html),
[cancelRebalanceTask](c/cancelRebalanceTask.html), [createIMOLTPTable](c/createIMOLTPTable.html), [cumdenseRank](c/cumdenseRank.html), [destroyMonitor](d/destroyMonitor.html), [enableTDEKey](e/enabletdekey.html), [flushPKEYCache](f/flushpkeycache.html), [genOutputColumnsForOBSnapshotEngine](g/genoutputcolumnsforobsnapshotengine.html), [generateMachineFingerprint](g/generateMachineFingerprint.html),
[geoWithin](g/geowithin.html), [getCacheEngineMemSize](g/getCacheEngineMemSize.html), [getCacheEngineStat](g/getCacheEngineStat.html), [getCachedSymbolBaseMemSize](g/getCachedSymbolBaseMemSize.html),
[getClusterTDEKeys](g/getclustertdekeys.html), [getControllerAlias](g/getControllerAlias.html), [getControllerElectionTick](g/getControllerElectionTick.html),
[getCurrentTDEKeyVersion](g/getcurrenttdekeyversion.html),
[getDfsRebalanceConcurrency](g/getDfsRebalanceConcurrency.html), [getDfsRecoveryConcurrency](g/getDfsRecoveryConcurrency.html),
[getEnableNullSafeJoin](g/getenablenullsafejoin.html),
[getEventListener](g/getEventListener.html), [getExecDir](g/getExecDir.html), [getIPConnectionLimit](g/getIPConnectionLimit.html), [getLoadedModules](g/getloadedmodules.html), [getOrcaCheckpointConfig](g/getOrcaCheckpointConfig.html),
[getOrcaCheckpointJobInfo](g/getOrcaCheckpointJobInfo.html),
[getOrcaCheckpointSubjobInfo](g/getOrcaCheckpointSubjobInfo.html),
[getOrcaDataLineage](g/getOrcaDataLineage.html),
[getOrcaStateMachineEventTaskStatus](g/getOrcaStateMachineEventTaskStatus.html),
[getOrcaStreamEngineMeta](g/getOrcaStreamEngineMeta.html),
[getOrcaStreamTaskSubscriptionMeta](g/getOrcaStreamTaskSubscriptionMeta.html),, [getRaftElectionTick](g/getRaftElectionTick.html), [getRaftLearnersStatus](g/getRaftLearnersStatus.html), [getRawScriptLog](g/getRawScriptLog.html), [getSessionExpiredTime](g/getsessionexpiredtime.html), [getSlaveReplicationExecutionStatus](g/getslavereplicationexecutionstatus.html), [getTSDBSortKeyEntry](g/getTSDBSortKeyEntry.html), [getTradingCalendarType](g/gettradingcalendartype.html), [getUdfEngineVariable](g/getUdfEngineVariable.html), [getWorkDir](g/getWorkDir.html), [initIMOLTPCheckpointEncryption](i/initimoltpcheckpointencryption.html), [isChunkNodeInit](i/isChunkNodeInit.html), [matrixRank](m/matrixRank.html),
[memSize](m/memSize.html), [objectComponent](o/objectComponent.html), [renameCatalogName](r/renameCatalogName.html), [resetDfsRebalanceConcurrency](r/resetDfsRebalanceConcurrency.html), [resetDfsRecoveryConcurrency](r/resetDfsRecoveryConcurrency.html), [resumeTimerEngine](r/resumeTimerEngine.html), [rotateTDEKey](r/rotatetdekey.html), [setDatabaseClusterReplicationExecutionSet](s/setdatabaseclusterreplicationexecutionset.html), [setIPConnectionLimit](s/setIPConnectionLimit.html), [setMaxTransactionSize](s/setMaxTransactionSize.html), [setOrcaCheckpointConfig](s/setOrcaCheckpointConfig.html), [setRaftElectionTick](s/setRaftElectionTick.html), [setSessionExpiredTime](s/setsessionexpiredtime.html), [setTableSensitiveColumn](s/setTableSensitiveColumn.html), [spawnMonitor](s/spawnMonitor.html), [stateMavg](s/stateMavg.html), [stopTimerEngine](s/stopTimerEngine.html), [terminate](t/terminate.html), [test](t/test.html), [triggerCheckpointForIMOLTP](t/triggercheckpointforimoltp.html), [triggerPKEYCompaction](t/triggerPKEYCompaction.html), [updateOrderBookEngineParams](u/updateOrderBookEngineParams.html), [updatePKEYDeleteBitmap](u/updatepkeydeletebitmap.html), [updateRule](u/updateRule.html), [writeLog](w/writeLog.html), [cancelConsoleJob](c/cancelConsoleJob.html), [cancelJob](c/cancelJob.html), [closeSessions](c/closeSessions.html), [defined](d/defined.html), [defs](d/defs.html), [deleteScheduledJob](d/deleteScheduledJob.html), [deleteMarketHoliday](d/deleteMarketHoliday.html), [deleteUser](d/deleteUser.html), [disableResourceTracking](d/disableresourcetracking.html),
[dumpHeapSample](d/dumpheapsample.html), [enableResourceTracking](e/enableresourcetracking.html),
[evalTimer](e/evalTimer.html), [getAclAuditlog](g/getaclauditlog.html), [getAuditLog](g/getauditlog.html), [getClusterPerf](g/getClusterPerf.html), [getConsoleJobs](g/getConsoleJobs.html), [getCurrentSessionAndUser](g/getCurrentSessionAndUser.html), [getDatanodeRestartInterval](g/getDatanodeRestartInterval.html),
[getDynamicConfig](g/getdynamicconfig.html), [getIPConnectionLimit](g/getIPConnectionLimit.html), [getJobMessage](g/getJobMessage.html), [getJobReturn](g/getJobReturn.html), [getJobStat](g/getJobStat.html), [getJobStatus](g/getJobStatus.html), [getLicenseExpiration](g/getLicenseExpiration.html), [getMemLimitOfAllTempResults](g/getmemlimitofalltempresults.html), [getPerf](g/getPerf.html),
[getRecentJobs](g/getRecentJobs.html), [getScheduledJobs](g/getScheduledJobs.html), [getSessionMemoryStat](g/getSessionMemoryStat.html), [getSupportBundle](g/getSupportBundle.html), [getTSDBDataStat](g/gettsdbdatastat.html), [getTSDBTableIndexCacheStatus](g/gettsdbtableindexcachestatus.html), [getUserHardwareUsage](g/getUserHardwareUsage.html), [getUserTableAccessRecords](g/getUserTableAccessRecords.html), [imtForceGCRedolog](i/imtForceGCRedolog.html), [imtUpdateChunkVersionOnDataNode](i/imtUpdateChunkVersionOnDataNode.html), [installPlugin](i/installPlugin.html), [license](l/license.html), [listRemotePlugins](l/listRemotePlugins.html), [loadModule](l/loadModule.html), [loadModuleFromScript](l/loadmodulefromscript.html), [loadPlugin](l/loadPlugin.html), [member](m/member.html), [module](../progr/statements/module.html),
[objByName](o/objByName.html), [objs](o/objs.html), [partial](p/partial.html), [pipeline](p/pipeline.html), [refCount](r/refCount.html), [saveModule](s/saveModule.html), [scheduleJob](s/scheduleJob.html), [setDatanodeRestartInterval](s/setDatanodeRestartInterval.html), [setDynamicConfig](s/setdynamicconfig.html), [,](s/setIPConnectionLimit.html) [setLogLevel](s/setLogLevel.html), [setMaxJobParallelism](s/setMaxJobParallelism.html), [setMaxJobPriority](s/setMaxJobPriority.html), [setMemLimitOfAllTempResults](s/setmemlimitofalltempresults.html), [setRandomSeed](s/setRandomSeed.html), [setRetentionPolicy](s/setRetentionPolicy.html), [setSystem](s/setSystem.html),
[startHeapSample](s/startheapsample.html),[stopHeapSample](s/stopheapsample.html),
[submitJob](s/submitJob.html), [submitJobEx](s/submitJobEx.html), [submitJobEx2](s/submitJobEx2.html), [syntax](s/syntax.html),
[timer](../progr/statements/timer.html), [undef](u/undef.html), [updateLicense](u/updateLicense.html), [use](../progr/statements/use.html),
[version](v/version.html), [getLoadedPlugins](g/getloadedplugins.html), [enableDynamicScriptOptimization](e/enabledynamicscriptoptimization.html), [disableDynamicScriptOptimization](d/disabledynamicscriptoptimization.html)[,](s/setIPConnectionLimit.html) [setLogLevel](s/setLogLevel.html)

## MCP

[addMCPPrompt](a/addMCPPrompt.html), [addMCPTool](a/addMCPTool.html), [callMCPTool](c/callMCPTool.html), [dropMCPPrompt](d/dropMCPPrompt.html), [dropMCPTool](d/dropMCPTool.html), [getMCPPrompt](g/getMCPPrompt.html), [listMCPPrompts](l/listMCPPrompts.html), [listMCPTools](l/listMCPTools.html), [publishMCPPrompts](p/publishMCPPrompts.html), [publishMCPTools](p/publishMCPTools.html), [updateMCPPrompt](u/updateMCPPrompt.html), [updateMCPTool](u/updateMCPTool.html), [withdrawMCPPrompts](w/withdrawMCPPrompts.html), [withdrawMCPTools](w/withdrawMCPTools.html)

## 环境

[clearAllCache](c/clearAllCache.html), [clearCachedDatabase](c/clearCachedDatabase.html), [clearCachedModules](c/clearCachedModules.html), [deleteChunkMetaOnMasterById](d/deletechunkmetaonmasterbyid.html), [deleteDataViewItems](d/deleteDataViewItems.html), [getDiskIOStat](g/getDiskIOStat.html), [getEnv](g/getEnv.html), [getHomeDir](g/getHomeDir.html), [getMemoryStat](g/getMemoryStat.html), [getOS](g/getOS.html), [getOSBit](g/getOSBit.html), [getSystemCpuUsage](g/getSystemCpuUsage.html), [getSystemLoadAvg](g/getSystemLoadAvg.html), [mem](m/mem.html), [moveHotDataToColdVolume](m/moveHotDataToColdVolume.html), [shell](s/shell.html),
[sleep](s/sleep.html), [clearAllIOTDBStaticTableCache](c/clearalliotdbstatictablecache.html), [clearAllIOTDBLatestKeyCache](c/clearalliotdblatestkeycache.html)

## 其它

[attributeNames](a/attributenames.html),
[attributeTypes](a/attributeTypes.html), [attributeValues](a/attributevalues.html),
[constantDesc](c/constantdesc.html), [convertExcelFormula](c/convertExcelFormula.html), [hmac](h/hmac.html), [genericStateIterate](g/genericStateIterate.html), [genericTStateIterate](g/genericTStateIterate.html), [objectChecksum](o/objectChecksum.html), [plot](p/plot.html), [plotHist](p/plotHist.html), [snippet](s/sinppet.html), [sqlTuple](s/sqlTuple.html)
