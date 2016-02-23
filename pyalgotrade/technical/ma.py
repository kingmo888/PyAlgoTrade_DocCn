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

import numpy as np
from pyalgotrade import technical
from pyalgotrade import dataseries


# This is the formula I'm using to calculate the averages based on previous ones.
# 1 2 3 4
# x x x
#   x x x
#
# avg0 = (a + b + c) / 3
# avg1 = (b + c + d) / 3
#
# avg0 = avg1 + x
# (a + b + c) / 3 = (b + c + d) / 3 + x
# a/3 + b/3 + c/3 = b/3 + c/3 + d/3 + x
# a/3 = d/3 + x
# x = a/3 - d/3

# avg1 = avg0 - x
# avg1 = avg0 + d/3 - a/3

class SMAEventWindow(technical.EventWindow):
    def __init__(self, period):
        assert(period > 0)
        technical.EventWindow.__init__(self, period)
        self.__value = None

    def onNewValue(self, dateTime, value):
        firstValue = None
        if len(self.getValues()) > 0:
            firstValue = self.getValues()[0]
            assert(firstValue is not None)

        technical.EventWindow.onNewValue(self, dateTime, value)

        if value is not None and self.windowFull():
            if self.__value is None:
                self.__value = self.getValues().mean()
            else:
                self.__value = self.__value + value / float(self.getWindowSize()) - firstValue / float(self.getWindowSize())

    def getValue(self):
        return self.__value


class SMA(technical.EventBasedFilter):
    """简单移动平均指标.

    :param dataSeries: 需要被计算指标的dataSeries.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: 周期
    :type period: int.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """
    def __init__(self, dataSeries, period, maxLen=dataseries.DEFAULT_MAX_LEN):
        technical.EventBasedFilter.__init__(self, dataSeries, SMAEventWindow(period), maxLen)


class EMAEventWindow(technical.EventWindow):
    def __init__(self, period):
        assert(period > 1)
        technical.EventWindow.__init__(self, period)
        self.__multiplier = (2.0 / (period + 1))
        self.__value = None

    def onNewValue(self, dateTime, value):
        technical.EventWindow.onNewValue(self, dateTime, value)

        # Formula from http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
        if value is not None and self.windowFull():
            if self.__value is None:
                self.__value = self.getValues().mean()
            else:
                self.__value = (value - self.__value) * self.__multiplier + self.__value

    def getValue(self):
        return self.__value


class EMA(technical.EventBasedFilter):
    """指数移动平均指标.

    :param dataSeries: 需要被计算指标的dataSeries.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: 周期。必须为大于1的整数
    :type period: int.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, maxLen=dataseries.DEFAULT_MAX_LEN):
        technical.EventBasedFilter.__init__(self, dataSeries, EMAEventWindow(period), maxLen)


class WMAEventWindow(technical.EventWindow):
    def __init__(self, weights):
        assert(len(weights) > 0)
        technical.EventWindow.__init__(self, len(weights))
        self.__weights = np.asarray(weights)

    def getValue(self):
        ret = None
        if self.windowFull():
            accum = (self.getValues() * self.__weights).sum()
            weightSum = self.__weights.sum()
            ret = accum / float(weightSum)
        return ret


class WMA(technical.EventBasedFilter):
    """加权移动平均指标.

    :param dataSeries: 需要被计算指标的dataSeries.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param weights: A list of int/float with the weights.
    :type weights: list.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, dataSeries, weights, maxLen=dataseries.DEFAULT_MAX_LEN):
        technical.EventBasedFilter.__init__(self, dataSeries, WMAEventWindow(weights), maxLen)