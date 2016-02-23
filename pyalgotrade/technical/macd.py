# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade.technical import ma
from pyalgotrade import dataseries


class MACD(dataseries.SequenceDataSeries):
    """MACD指标的定义： http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_average_conve.

    :param dataSeries: 需要被计算指标的dataSeries.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param fastEMA: 快线移动平均线参数
    :type fastEMA: int.
    :param slowEMA: 慢线移动平均线参数
    :type slowEMA: int.
    :param signalEMA: 移动平均线参数
    :type signalEMA: int.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """
    def __init__(self, dataSeries, fastEMA, slowEMA, signalEMA, maxLen=dataseries.DEFAULT_MAX_LEN):
        assert(fastEMA > 0)
        assert(slowEMA > 0)
        assert(fastEMA < slowEMA)
        assert(signalEMA > 0)

        dataseries.SequenceDataSeries.__init__(self, maxLen)

        # We need to skip some values when calculating the fast EMA in order for both EMA
        # to calculate their first values at the same time.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__fastEMASkip = slowEMA - fastEMA

        self.__fastEMAWindow = ma.EMAEventWindow(fastEMA)
        self.__slowEMAWindow = ma.EMAEventWindow(slowEMA)
        self.__signalEMAWindow = ma.EMAEventWindow(signalEMA)
        self.__signal = dataseries.SequenceDataSeries(maxLen)
        self.__histogram = dataseries.SequenceDataSeries(maxLen)
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def getSignal(self):
        """返回MACD的 :class:`pyalgotrade.dataseries.DataSeries` 类型的移动平均线."""
        return self.__signal

    def getHistogram(self):
        """返回:class:`pyalgotrade.dataseries.DataSeries` 类型的直方图 (the difference between the MACD and the Signal)."""
        return self.__histogram

    def __onNewValue(self, dataSeries, dateTime, value):
        diff = None
        macdValue = None
        signalValue = None
        histogramValue = None

        # We need to skip some values when calculating the fast EMA in order for both EMA
        # to calculate their first values at the same time.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__slowEMAWindow.onNewValue(dateTime, value)
        if self.__fastEMASkip > 0:
            self.__fastEMASkip -= 1
        else:
            self.__fastEMAWindow.onNewValue(dateTime, value)
            if self.__fastEMAWindow.windowFull():
                diff = self.__fastEMAWindow.getValue() - self.__slowEMAWindow.getValue()

        # Make the first MACD value available as soon as the first signal value is available.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__signalEMAWindow.onNewValue(dateTime, diff)
        if self.__signalEMAWindow.windowFull():
            macdValue = diff
            signalValue = self.__signalEMAWindow.getValue()
            histogramValue = macdValue - signalValue

        self.appendWithDateTime(dateTime, macdValue)
        self.__signal.appendWithDateTime(dateTime, signalValue)
        self.__histogram.appendWithDateTime(dateTime, histogramValue)
