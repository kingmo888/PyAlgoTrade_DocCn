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

from pyalgotrade.utils import collections
from pyalgotrade import dataseries


class EventWindow(object):
    """事件窗口类负责在一个移动滑窗中进行计算。

    :param windowSize: 滑窗的大小。必须大于0。
    :type windowSize: int.
    :param dtype: 数组所需的数据类型
    :type dtype: data-type.
    :param skipNone: 是否跳过空值。默认为True 。一般在滑窗中不含空值的情况下使用True。
    :type skipNone: boolean.

    .. note::
        这是一个基类，不应该直接被调用.
    """

    def __init__(self, windowSize, dtype=float, skipNone=True):
        assert(windowSize > 0)
        assert(isinstance(windowSize, int))
        self.__values = collections.NumPyDeque(windowSize, dtype)
        self.__windowSize = windowSize
        self.__skipNone = skipNone

    def onNewValue(self, dateTime, value):
        if value is not None or not self.__skipNone:
            self.__values.append(value)

    def getValues(self):
        """Returns a numpy.array with the values in the window."""
        return self.__values.data()

    def getWindowSize(self):
        """返回滑窗的大小"""
        return self.__windowSize

    def windowFull(self):
        return len(self.__values) == self.__windowSize

    def getValue(self):
        """通过滑窗中的值来计算一个值"""
        raise NotImplementedError()


class EventBasedFilter(dataseries.SequenceDataSeries):
    """EventBasedFilter 类负责接收一个 :class:`pyalgotrade.dataseries.DataSeries` 类型的新值
    并通过 :class:`EventWindow` 来计算一个新值。

    :param dataSeries: 需要被计算指标的DataSeries实例。
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param eventWindow: 用于计算新值的EventWindow实例。
    :type eventWindow: :class:`EventWindow`.
    :param 存放的最大值。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, dataSeries, eventWindow, maxLen=dataseries.DEFAULT_MAX_LEN):
        dataseries.SequenceDataSeries.__init__(self, maxLen)
        self.__dataSeries = dataSeries
        self.__dataSeries.getNewValueEvent().subscribe(self.__onNewValue)
        self.__eventWindow = eventWindow

    def __onNewValue(self, dataSeries, dateTime, value):
        # Let the event window perform calculations.
        self.__eventWindow.onNewValue(dateTime, value)
        # Get the resulting value
        newValue = self.__eventWindow.getValue()
        # Add the new value.
        self.appendWithDateTime(dateTime, newValue)

    def getDataSeries(self):
        return self.__dataSeries

    def getEventWindow(self):
        return self.__eventWindow
