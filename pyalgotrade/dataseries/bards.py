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

from pyalgotrade import dataseries


class BarDataSeries(dataseries.SequenceDataSeries):
    """一个 :class:`pyalgotrade.bar.Bar` 的实例DataSeries.

    :param maxLen: 驻留的最大数量。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, maxLen=dataseries.DEFAULT_MAX_LEN):
        dataseries.SequenceDataSeries.__init__(self, maxLen)
        self.__openDS = dataseries.SequenceDataSeries(maxLen)
        self.__closeDS = dataseries.SequenceDataSeries(maxLen)
        self.__highDS = dataseries.SequenceDataSeries(maxLen)
        self.__lowDS = dataseries.SequenceDataSeries(maxLen)
        self.__volumeDS = dataseries.SequenceDataSeries(maxLen)
        self.__adjCloseDS = dataseries.SequenceDataSeries(maxLen)
        self.__useAdjustedValues = False

    def setUseAdjustedValues(self, useAdjusted):
        self.__useAdjustedValues = useAdjusted

    def append(self, bar):
        self.appendWithDateTime(bar.getDateTime(), bar)

    def appendWithDateTime(self, dateTime, bar):
        assert(dateTime is not None)
        assert(bar is not None)
        bar.setUseAdjustedValue(self.__useAdjustedValues)
        dataseries.SequenceDataSeries.appendWithDateTime(self, dateTime, bar)
        self.__openDS.appendWithDateTime(dateTime, bar.getOpen())
        self.__closeDS.appendWithDateTime(dateTime, bar.getClose())
        self.__highDS.appendWithDateTime(dateTime, bar.getHigh())
        self.__lowDS.appendWithDateTime(dateTime, bar.getLow())
        self.__volumeDS.appendWithDateTime(dateTime, bar.getVolume())
        self.__adjCloseDS.appendWithDateTime(dateTime, bar.getAdjClose())

    def getOpenDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的开盘价序列"""
        return self.__openDS

    def getCloseDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的收盘价序列"""
        return self.__closeDS

    def getHighDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的最高价序列"""
        return self.__highDS

    def getLowDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的最低价序列"""
        return self.__lowDS

    def getVolumeDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的成交量序列"""
        return self.__volumeDS

    def getAdjCloseDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的复权价序列"""
        return self.__adjCloseDS

    def getPriceDataSeries(self):
        """返回 :class:`pyalgotrade.dataseries.DataSeries` 的收盘价或者复权收盘价序列（根据是否启用复权决定）"""
        if self.__useAdjustedValues:
            return self.__adjCloseDS
        else:
            return self.__closeDS
