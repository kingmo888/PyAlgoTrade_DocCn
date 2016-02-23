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


class VWAPEventWindow(technical.EventWindow):
    def __init__(self, windowSize, useTypicalPrice):
        technical.EventWindow.__init__(self, windowSize, dtype=object)
        self.__useTypicalPrice = useTypicalPrice

    def getValue(self):
        ret = None
        if self.windowFull():
            cumTotal = 0
            cumVolume = 0

            for bar in self.getValues():
                if self.__useTypicalPrice:
                    cumTotal += bar.getTypicalPrice() * bar.getVolume()
                else:
                    cumTotal += bar.getClose() * bar.getVolume()
                cumVolume += bar.getVolume()

            ret = cumTotal / float(cumVolume)
        return ret


class VWAP(technical.EventBasedFilter):
    """成交加权平均价指标.

    :param dataSeries: 需要被计算指标的dataSeries.
    :type dataSeries: :class:`pyalgotrade.dataseries.bards.BarDataSeries`.
    :param period: 用于计算VWAP的长度.
    :type period: int.
    :param useTypicalPrice: 默认为假。是否用典型价代替收盘价。
    :type useTypicalPrice: boolean.
    :param maxLen: 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, useTypicalPrice=False, maxLen=dataseries.DEFAULT_MAX_LEN):
        assert isinstance(dataSeries, bards.BarDataSeries), \
            "dataSeries must be a dataseries.bards.BarDataSeries instance"

        technical.EventBasedFilter.__init__(self, dataSeries, VWAPEventWindow(period, useTypicalPrice), maxLen)

    def getPeriod(self):
        return self.getWindowSize()
