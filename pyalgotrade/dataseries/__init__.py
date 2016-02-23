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

import abc

from pyalgotrade import observer
from pyalgotrade.utils import collections

DEFAULT_MAX_LEN = 1024


# It is important to inherit object to get __getitem__ to work properly.
# Check http://code.activestate.com/lists/python-list/621258/
class DataSeries(object, metaclass=abc.ABCMeta):
    """Base class for data series.

    .. note::
        这是一个基类，不应该直接被调用.
    """

    @abc.abstractmethod
    def __len__(self):
        """Returns the number of elements in the data series."""
        raise NotImplementedError()

    def __getitem__(self, key):
        """Returns the value at a given position/slice. It raises IndexError if the position is invalid,
        or TypeError if the key type is invalid."""
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key >= len(self) or key < 0:
                raise IndexError("Index out of range")
            return self.getValueAbsolute(key)
        else:
            raise TypeError("Invalid argument type")

    # This is similar to __getitem__ for ints, but it shouldn't raise for invalid positions.
    @abc.abstractmethod
    def getValueAbsolute(self, pos):
        raise NotImplementedError()

    @abc.abstractmethod
    def getDateTimes(self):
        """Returns a list of :class:`datetime.datetime` associated with each value."""
        raise NotImplementedError()


class SequenceDataSeries(DataSeries):
    """一个在内存序列中存放的DataSeries.

    :param maxLen: 允许驻留的最大数量。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.
    """

    def __init__(self, maxLen=DEFAULT_MAX_LEN):
        if not maxLen > 0:
            raise Exception("Invalid maximum length")

        self.__newValueEvent = observer.Event()
        self.__values = collections.ListDeque(maxLen)
        self.__dateTimes = collections.ListDeque(maxLen)

    def __len__(self):
        return len(self.__values)

    def __getitem__(self, key):
        return self.__values[key]

    def setMaxLen(self, maxLen):
        """调整允许驻留的最大数量"""
        self.__values.resize(maxLen)
        self.__dateTimes.resize(maxLen)

    def getMaxLen(self):
        """返回允许驻留的最大数量"""
        return self.__values.getMaxLen()

    # 事件处理句柄接收：:
    # 1: Dataseries 触发事件
    # 2: 新值的datetime
    # 3: 新值
    def getNewValueEvent(self):
        return self.__newValueEvent

    def getValueAbsolute(self, pos):
        ret = None
        if pos >= 0 and pos < len(self.__values):
            ret = self.__values[pos]
        return ret

    def append(self, value):
        """添加一个值."""
        self.appendWithDateTime(None, value)

    def appendWithDateTime(self, dateTime, value):
        """
        添加一个带dateTime的值.

        .. note::
            如果dateTime非None，它必须大于原队列最后一个值。
        """

        if dateTime is not None and len(self.__dateTimes) != 0 and self.__dateTimes[-1] >= dateTime:
            raise Exception("Invalid datetime. It must be bigger than that last one")

        assert(len(self.__values) == len(self.__dateTimes))
        self.__dateTimes.append(dateTime)
        self.__values.append(value)

        self.getNewValueEvent().emit(self, dateTime, value)

    def getDateTimes(self):
        return self.__dateTimes.data()
