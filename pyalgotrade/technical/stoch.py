# encoding:utf-8
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

from pyalgotrade import technical
from pyalgotrade import dataseries
from pyalgotrade.dataseries import bards
from pyalgotrade.technical import ma


class BarWrapper(object):
    def __init__(self, useAdjusted):
        self.__useAdjusted = useAdjusted

    def getLow(self, bar_):
        return bar_.getLow(self.__useAdjusted)

    def getHigh(self, bar_):
        return bar_.getHigh(self.__useAdjusted)

    def getClose(self, bar_):
        return bar_.getClose(self.__useAdjusted)


def get_low_high_values(barWrapper, bars):
    currBar = bars[0]
    lowestLow = barWrapper.getLow(currBar)
    highestHigh = barWrapper.getHigh(currBar)
    for i in range(len(bars)):
        currBar = bars[i]
        lowestLow = min(lowestLow, barWrapper.getLow(currBar))
        highestHigh = max(highestHigh, barWrapper.getHigh(currBar))
    return (lowestLow, highestHigh)


class SOEventWindow(technical.EventWindow):
    def __init__(self, period, useAdjustedValues):
        assert(period > 1)
        technical.EventWindow.__init__(self, period, dtype=object)
        self.__barWrapper = BarWrapper(useAdjustedValues)

    def getValue(self):
        ret = None
        if self.windowFull():
            lowestLow, highestHigh = get_low_high_values(self.__barWrapper, self.getValues())
            currentClose = self.__barWrapper.getClose(self.getValues()[-1])
            ret = (currentClose - lowestLow) / float(highestHigh - lowestLow) * 100
        return ret


class StochasticOscillator(technical.EventBasedFilter):
    """随机振荡指标定义：
    http://stockcharts.com/school/doku.php?st=stochastic+oscillator&id=chart_school:technical_indicators:stochastic_oscillator_fast_slow_and_full.
    Note that the value returned by this filter is %K. To access %D use :meth:`getD`.

    :param barDataSeries: 需要被计算指标的dataSeries.
    :type barDataSeries: :class:`pyalgotrade.dataseries.bards.BarDataSeries`.
    :param period: 周期. 必须大于1.
    :type period: int.
    :param dSMAPeriod: The %D SMA period. Must be > 1.
    :type dSMAPeriod: int.
    :param useAdjustedValues: 默认为假。是否用Low/High/Close的复权价.
    :type useAdjustedValues: boolean.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, barDataSeries, period, dSMAPeriod=3, useAdjustedValues=False, maxLen=dataseries.DEFAULT_MAX_LEN):
        assert dSMAPeriod > 1, "dSMAPeriod must be > 1"
        assert isinstance(barDataSeries, bards.BarDataSeries), \
            "barDataSeries must be a dataseries.bards.BarDataSeries instance"

        technical.EventBasedFilter.__init__(self, barDataSeries, SOEventWindow(period, useAdjustedValues), maxLen)
        self.__d = ma.SMA(self, dSMAPeriod, maxLen)

    def getD(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 类型的 %D 值."""
        return self.__d
