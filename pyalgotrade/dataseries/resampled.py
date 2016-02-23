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

import abc

from pyalgotrade import dataseries
from pyalgotrade.dataseries import bards
from pyalgotrade import bar
from pyalgotrade import resamplebase


class AggFunGrouper(resamplebase.Grouper):
    def __init__(self, groupDateTime, value, aggfun):
        resamplebase.Grouper.__init__(self, groupDateTime)
        self.__values = [value]
        self.__aggfun = aggfun

    def addValue(self, value):
        self.__values.append(value)

    def getGrouped(self):
        return self.__aggfun(self.__values)


class BarGrouper(resamplebase.Grouper):
    def __init__(self, groupDateTime, bar_, frequency):
        resamplebase.Grouper.__init__(self, groupDateTime)
        self.__open = bar_.getOpen()
        self.__high = bar_.getHigh()
        self.__low = bar_.getLow()
        self.__close = bar_.getClose()
        self.__volume = bar_.getVolume()
        self.__adjClose = bar_.getAdjClose()
        self.__useAdjValue = bar_.getUseAdjValue()
        self.__frequency = frequency

    def addValue(self, value):
        self.__high = max(self.__high, value.getHigh())
        self.__low = min(self.__low, value.getLow())
        self.__close = value.getClose()
        self.__adjClose = value.getAdjClose()
        self.__volume += value.getVolume()

    def getGrouped(self):
        """Return the grouped value."""
        ret = bar.BasicBar(
            self.getDateTime(),
            self.__open,
            self.__high,
            self.__low,
            self.__close,
            self.__volume,
            self.__adjClose,
            self.__frequency
        )
        ret.setUseAdjustedValue(self.__useAdjValue)
        return ret


class DSResampler(object, metaclass=abc.ABCMeta):
    def __init__(self, dataSeries, frequency):
        if not resamplebase.is_valid_frequency(frequency):
            raise Exception("Unsupported frequency")

        self.__frequency = frequency
        self.__grouper = None
        self.__range = None

        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    @abc.abstractmethod
    def buildGrouper(self, range_, value, frequency):
        raise NotImplementedError()

    def __onNewValue(self, dataSeries, dateTime, value):
        if self.__range is None:
            self.__range = resamplebase.build_range(dateTime, self.__frequency)
            self.__grouper = self.buildGrouper(self.__range, value, self.__frequency)
        elif self.__range.belongs(dateTime):
            self.__grouper.addValue(value)
        else:
            self.appendWithDateTime(self.__grouper.getDateTime(), self.__grouper.getGrouped())
            self.__range = resamplebase.build_range(dateTime, self.__frequency)
            self.__grouper = self.buildGrouper(self.__range, value, self.__frequency)

    def pushLast(self):
        if self.__grouper is not None:
            self.appendWithDateTime(self.__grouper.getDateTime(), self.__grouper.getGrouped())
            self.__grouper = None
            self.__range = None

    def checkNow(self, dateTime):
        if self.__range is not None and not self.__range.belongs(dateTime):
            self.appendWithDateTime(self.__grouper.getDateTime(), self.__grouper.getGrouped())
            self.__grouper = None
            self.__range = None


class ResampledBarDataSeries(bards.BarDataSeries, DSResampler):
    """创建一个更大频率的BarDataSeries，并将其作为一个新值推送到被重采样的位置。

    :param dataSeries: 需要被重采样的DataSeries
    :type dataSeries: :class:`pyalgotrade.dataseries.bards.BarDataSeries`
    :param frequency: 用于分组的秒级频率。必须大于0。
    :param maxLen: 驻留的最大数量。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.

    .. note::
        * 支持的重采样频率范围:
            * 日线以下频率
            * 日线（bar.Frequency.DAY）
            * 月线（bar.Frequency.MONTH）
    """

    def __init__(self, dataSeries, frequency, maxLen=dataseries.DEFAULT_MAX_LEN):
        if not isinstance(dataSeries, bards.BarDataSeries):
            raise Exception("dataSeries must be a dataseries.bards.BarDataSeries instance")

        bards.BarDataSeries.__init__(self, maxLen)
        DSResampler.__init__(self, dataSeries, frequency)

    def checkNow(self, dateTime):
        """强制重采样检查。 根据重采样频率、当前时间产生一个新值。

       :param dateTime: 当前时间
       :type dateTime: :class:`datetime.datetime`
        """

        return DSResampler.checkNow(self, dateTime)

    def buildGrouper(self, range_, value, frequency):
        return BarGrouper(range_.getBeginning(), value, frequency)


class ResampledDataSeries(dataseries.SequenceDataSeries, DSResampler):
    def __init__(self, dataSeries, frequency, aggfun, maxLen=dataseries.DEFAULT_MAX_LEN):
        dataseries.SequenceDataSeries.__init__(self, maxLen)
        DSResampler.__init__(self, dataSeries, frequency)
        self.__aggfun = aggfun

    def buildGrouper(self, range_, value, frequency):
        return AggFunGrouper(range_.getBeginning(), value, self.__aggfun)
